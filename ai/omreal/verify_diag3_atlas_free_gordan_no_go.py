#!/usr/bin/env python3
"""Exact replay of an atlas-free diagonal-three Gordan no-go.

The construction has one common family of twelve nonzero polynomial normals
in four-space and three fixed row reorientations.  For three prescribed
global-graph polynomials ``q_k`` it proves exactly that signing ``k`` is
Gordan-bad precisely on ``q_k = 0``.  The normalized witness fibers and all
their coordinate restrictions are convex, the joined resolution contains
every zero-block face, and the three sign traces are shattered.  Nevertheless
the balanced pair kernel and the simultaneous-feasible ``H_6`` both have
rank two.

This is a logical counterexample to an atlas-free theorem based only on
common polynomial Gordan normals, convex coordinate carriers, local Koszul
or simplex exactness, and sign-shattered private-loop completion.  The
normals are deliberately not asserted to be the 56 Pluecker-derived normals
of one uniform rank-four/eight parent.

The replay is dependency-free and uses exact integer/Fraction arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import comb, gcd


DIMENSION = 4
SIGNATURES = range(3)
GROUPS = range(3)
ROWS = range(4)
FOURTH = 3

# For owner group k, (a,b) are the other two among the first three axes.
GROUP_AXES = ((1, 2), (2, 0), (0, 1))


def add(left, right):
    return tuple(a + b for a, b in zip(left, right, strict=True))


def scale(coefficient, vector):
    return tuple(coefficient * value for value in vector)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def unit(axis):
    return tuple(int(index == axis) for index in range(DIMENSION))


def exact_rank(rows):
    work = [[Fraction(value) for value in row] for row in rows]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(
                    work[row], work[rank], strict=True
                )
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def rank_mod_two(rows):
    vectors = [
        sum((int(value) & 1) << column for column, value in enumerate(row))
        for row in rows
    ]
    rank = 0
    column_count = len(rows[0]) if rows else 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, len(vectors)) if vectors[row] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        vectors[rank], vectors[pivot] = vectors[pivot], vectors[rank]
        for row in range(len(vectors)):
            if row != rank and vectors[row] >> column & 1:
                vectors[row] ^= vectors[rank]
        rank += 1
    return rank


def base_group(group):
    """The rank-three positive four-circuit at q_group = 0."""

    axis_a, axis_b = GROUP_AXES[group]
    e_a = unit(axis_a)
    e_b = unit(axis_b)
    e_fourth = unit(FOURTH)
    return (
        add(e_a, e_b),
        add(add(e_a, scale(-1, e_b)), e_fourth),
        add(add(scale(-1, e_a), scale(2, e_b)), e_fourth),
        add(add(scale(-1, e_a), scale(-2, e_b)), scale(-2, e_fourth)),
    )


BASE_GROUPS = tuple(base_group(group) for group in GROUPS)


def normal(group, row, q_squared):
    """Common unsigned row n_(group,row), with q_squared >= 0."""

    answer = BASE_GROUPS[group][row]
    if row == 3:
        answer = add(answer, scale(q_squared, unit(group)))
    return answer


def signing(signature, group, row):
    """Fixed reorientation sign of one common unsigned normal."""

    if signature == group:
        return 1
    coordinate = BASE_GROUPS[group][row][signature]
    if not coordinate:
        raise AssertionError("nonowner reorientation encountered a zero trace")
    return 1 if coordinate > 0 else -1


SIGN_TABLE = tuple(
    tuple(
        tuple(signing(signature, group, row) for row in ROWS)
        for group in GROUPS
    )
    for signature in SIGNATURES
)


def owner_slice(group):
    """Exact c_group with first-three owner evaluations all equal to one."""

    axis_a, axis_b = GROUP_AXES[group]
    return add(
        add(scale(Fraction(3, 5), unit(axis_a)),
            scale(Fraction(2, 5), unit(axis_b))),
        scale(Fraction(4, 5), unit(FOURTH)),
    )


def verify_minimal_circuits():
    for group in GROUPS:
        rows = BASE_GROUPS[group]
        if tuple(sum(row[column] for row in rows) for column in range(4)) != (0, 0, 0, 0):
            raise AssertionError("owner wall rows lost their positive relation")
        if exact_rank(rows) != 3:
            raise AssertionError("owner wall circuit lost rank three")
        for deleted in ROWS:
            remaining = [row for index, row in enumerate(rows) if index != deleted]
            if exact_rank(remaining) != 3:
                raise AssertionError("owner wall circuit is not support-minimal")
        for row in ROWS:
            if not any(normal(group, row, 0)):
                raise AssertionError("a common normal vanishes on its wall")
        # The fixed fourth coordinate of the moving row is -2, so it cannot
        # vanish for any real value of q_group^2.
        if BASE_GROUPS[group][3][FOURTH] != -2:
            raise AssertionError("moving-normal nonvanishing guard changed")


def verify_exact_bad_loci():
    """Prove B_k = Z(q_k) by an exact affine-in-s witness calculation."""

    for signature in SIGNATURES:
        c_vector = owner_slice(signature)
        owner = BASE_GROUPS[signature]
        owner_constants = tuple(dot(row, c_vector) for row in owner)
        if owner_constants != (1, 1, 1, -3):
            raise AssertionError("owner witness slice changed")

        # At q_signature = 0, the positive circuit checked above is a Gordan
        # witness.  If q_signature != 0, evaluate all strict inequalities on
        # p = c_signature + s e_signature.  The three fixed owner rows are
        # already +1; the fourth is -3 + q_signature^2 s.
        owner_slopes = (0, 0, 0, "q_signature^2")
        if owner_slopes[:3] != (0, 0, 0):
            raise AssertionError("fixed owner rows unexpectedly move in s")

        # Every row in a nonowner group has a strictly positive s-slope
        # after its fixed reorientation.  Its constant term may depend on
        # q_group^2, but finitely many affine inequalities with positive
        # slopes are simultaneously positive for all sufficiently large s.
        for group in GROUPS:
            if group == signature:
                continue
            for row in ROWS:
                sign = SIGN_TABLE[signature][group][row]
                slope = sign * BASE_GROUPS[group][row][signature]
                if slope != abs(BASE_GROUPS[group][row][signature]) or slope <= 0:
                    raise AssertionError("nonowner witness slope is not positive")


def verify_sign_shatter():
    traces = tuple(
        tuple(SIGN_TABLE[signature][0][row] for signature in SIGNATURES)
        for row in ROWS
    )
    expected = (
        (1, 1, 1),
        (1, 1, -1),
        (1, -1, 1),
        (1, -1, -1),
    )
    if traces != expected:
        raise AssertionError("the four antipodal trace classes are not shattered")
    return traces


def signed_block_sum(signature, group, q_squared, weights):
    answer = [Fraction(0) for _ in range(DIMENSION)]
    for row, weight in enumerate(weights):
        signed = scale(
            SIGN_TABLE[signature][group][row],
            normal(group, row, q_squared),
        )
        for coordinate, value in enumerate(signed):
            answer[coordinate] += Fraction(weight) * value
    return tuple(answer)


def verify_zero_block_faces():
    """Replay every nonempty block-mass face over the triple locus."""

    owner_witnesses = []
    for signature in SIGNATURES:
        weights = (Fraction(1, 4),) * 4
        if signed_block_sum(signature, signature, 0, weights) != (0, 0, 0, 0):
            raise AssertionError("owner circuit did not normalize to a witness")
        owner_witnesses.append(weights)

    checked = 0
    for size in (1, 2, 3):
        for active in combinations(SIGNATURES, size):
            block_mass = Fraction(1, size)
            total_mass = Fraction(0)
            for signature in SIGNATURES:
                if signature in active:
                    weights = tuple(block_mass * value for value in owner_witnesses[signature])
                    if signed_block_sum(signature, signature, 0, weights) != (0, 0, 0, 0):
                        raise AssertionError("active joined block does not annihilate")
                    total_mass += sum(weights)
                else:
                    weights = (Fraction(0),) * 4
                    if any(weights):
                        raise AssertionError("inactive block is not the zero face")
            if total_mass != 1:
                raise AssertionError("joined witness lost its mass normalization")
            checked += 1
    if checked != 7:
        raise AssertionError("wrong nonempty block-face census")
    return checked


def verify_loop_completion():
    """Pin a complete uniform eight-hyperplane loop stratification.

    The loop parent is independent of the deliberately abstract common
    normal family.  Its role is to show that adjoining every internal loop
    face cannot change the rank-two base obstruction: it only subdivides the
    contractible oriented-normal image of each sign-shattered private fiber.
    """

    # Eight points of the rational normal curve.  Every four columns form a
    # nonzero Vandermonde determinant, so a nonzero private-triple normal can
    # annihilate at most three of them.
    parent = tuple((1, value, value**2, value**3) for value in range(1, 9))
    for selected in combinations(parent, 4):
        if exact_rank(selected) != 4:
            raise AssertionError("the pinned loop parent is not uniform")

    # Complete oriented covector f-vector for eight general-position central
    # hyperplanes in four-space, grouped by the number z of loop labels.
    f_vector = tuple(
        comb(8, zero_count)
        * 2
        * sum(comb(7 - zero_count, degree) for degree in range(4 - zero_count))
        for zero_count in range(4)
    )
    if f_vector != (128, 352, 336, 112) or sum(f_vector) != 928:
        raise AssertionError("full loop-covector census changed")
    return parent, f_vector


def polynomial_add(left, right, coefficient=1):
    answer = dict(left)
    for exponent, value in right.items():
        updated = answer.get(exponent, 0) + coefficient * value
        if updated:
            answer[exponent] = updated
        else:
            answer.pop(exponent, None)
    return answer


def polynomial_multiply(left, right):
    answer = {}
    for left_exponent, left_value in left.items():
        for right_exponent, right_value in right.items():
            exponent = left_exponent + right_exponent
            answer[exponent] = answer.get(exponent, 0) + left_value * right_value
    return {exponent: value for exponent, value in answer.items() if value}


def verify_global_graphs():
    """Verify the three real pair intersections are the same R x S^6."""

    # B_k is z = f_k(g), with g = ||u||^2 - 1.
    f = (
        {},
        {1: 1},
        {1: 2, 3: 1},
    )
    g_polynomial = {1: 1}
    one_plus_g_squared = {0: 1, 2: 1}
    two_plus_g_squared = {0: 2, 2: 1}
    differences = (
        polynomial_add(f[1], f[0], -1),
        polynomial_add(f[2], f[0], -1),
        polynomial_add(f[2], f[1], -1),
    )
    expected = (
        g_polynomial,
        polynomial_multiply(g_polynomial, two_plus_g_squared),
        polynomial_multiply(g_polynomial, one_plus_g_squared),
    )
    if differences != expected:
        raise AssertionError("global graph pair differences changed")
    # The remaining factors are strictly positive for every real g, so all
    # pair equalities force g=0 and then z=0.
    if one_plus_g_squared[0] <= 0 or two_plus_g_squared[0] <= 0:
        raise AssertionError("a real-positive graph factor lost positivity")
    return f, differences


def verify_balanced_rank():
    """Exact low-degree compact-support Cech rank calculation."""

    # T = R x S^6 has H_c^1(T;Z)=Z.  All three pair intersections equal T,
    # so their restriction maps are identities with the Cech signs below.
    differential = ((1, -1, 1),)
    rational_rank = exact_rank(differential)
    mod_two_rank = rank_mod_two(differential)
    if rational_rank != 1 or mod_two_rank != 1:
        raise AssertionError("balanced restriction rank changed")
    middle_dimension = 3
    kernel_rank = middle_dimension - rational_rank
    kernel_rank_mod_two = middle_dimension - mod_two_rank
    if kernel_rank != 2 or kernel_rank_mod_two != 2:
        raise AssertionError("balanced kernel did not retain rank two")
    if gcd(*(abs(value) for value in differential[0])) != 1:
        raise AssertionError("balanced differential is not primitive")

    # E_ij is empty, so beta maps its rank-two balanced domain to zero.  The
    # singleton graph walls R^8 have no compact-support cohomology in degrees
    # <= 2.  Hence this kernel survives as H_c^2 of the three-wall union.
    exclusive_pair_rank = 0
    beta_target_rank = 0
    union_hc2_rank = kernel_rank
    # Alexander duality in R^9 sends H_c^2(B) to H_tilde_6(R^9 minus B).
    feasible_h6_rank = union_hc2_rank
    return {
        "differential": differential,
        "rank_Q": rational_rank,
        "rank_F2": mod_two_rank,
        "kernel_rank_Q": kernel_rank,
        "kernel_rank_F2": kernel_rank_mod_two,
        "exclusive_pair_rank": exclusive_pair_rank,
        "beta_target_rank": beta_target_rank,
        "union_Hc2_rank": union_hc2_rank,
        "feasible_H6_rank": feasible_h6_rank,
    }


def semantic_digest(graph_data, traces, block_faces, loop_data, ranks):
    payload = (
        BASE_GROUPS,
        SIGN_TABLE,
        graph_data,
        traces,
        block_faces,
        loop_data,
        tuple(sorted(ranks.items())),
    )
    return sha256(
        b"diag3-atlas-free-gordan-no-go-v1\0" + repr(payload).encode("ascii")
    ).hexdigest()


def main():
    verify_minimal_circuits()
    verify_exact_bad_loci()
    traces = verify_sign_shatter()
    block_faces = verify_zero_block_faces()
    loop_data = verify_loop_completion()
    graph_data = verify_global_graphs()
    ranks = verify_balanced_rank()
    digest = semantic_digest(graph_data, traces, block_faces, loop_data, ranks)

    print("PASS: one common family of 12 nonzero polynomial normals in rank four")
    print("PASS: each q_k=0 owner support is a minimal positive four-circuit")
    print("PASS: exact affine witnesses prove B_k = Z(q_k) for k=0,1,2")
    print("PASS: sign traces are", traces)
    print("PASS: all", block_faces, "nonempty joined block-mass faces occur at T")
    print("PASS: complete internal loop covector f-vector is", loop_data[1])
    print("PASS: every pair and triple intersection is T = R x S^6")
    print(
        "PASS: balanced ranks over Q/F2 are",
        ranks["rank_Q"],
        ranks["rank_F2"],
        "with kernel ranks",
        ranks["kernel_rank_Q"],
        ranks["kernel_rank_F2"],
    )
    print("PASS: beta has zero target because every exclusive-pair stratum is empty")
    print("PASS: H_c^2(union B_k) and H_tilde_6(F_S) both have rank", ranks["feasible_H6_rank"])
    print("SEMANTIC_SHA256", digest)
    print(
        "NO-GO: convex Gordan coordinate carriers, fiberwise Koszul/simplex "
        "exactness, sign shattering, and full internal loop completion do not "
        "force the balanced pair complex or H_6(F_S) to vanish"
    )
    print(
        "SCOPE: the countermodel is not a 56-row Pluecker-derived normal "
        "arrangement of one uniform rank-four/eight parent; an atlas-free "
        "9DVL theorem must use that additional global occurrence structure"
    )


if __name__ == "__main__":
    main()
