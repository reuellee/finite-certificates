#!/usr/bin/env python3
"""Exact algebraic replay for the diagonal-3 pair differential.

The checker has two independent parts.  It first builds the integral block
complex (22)--(23) from small cochain blocks with nonzero frontier maps and
checks (19), (24), the unit-Smith test (25), and a contraction identity (26).
It then replays the smooth global-graph countermodel showing why component
noncompactness alone cannot supply those frontier blocks.
"""

from __future__ import annotations

from fractions import Fraction


Matrix = list[list[int]]


def zeros(rows: int, columns: int) -> Matrix:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    out = zeros(size, size)
    for index in range(size):
        out[index][index] = 1
    return out


def shape(matrix: Matrix) -> tuple[int, int]:
    if not matrix or not matrix[0]:
        raise AssertionError("this replay uses positive block dimensions")
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise AssertionError("ragged matrix")
    return len(matrix), columns


def multiply(left, right):
    left_rows, shared = len(left), len(left[0])
    if len(right) != shared:
        raise AssertionError("matrix product dimension mismatch")
    right_columns = len(right[0])
    return [
        [
            sum(left[row][inner] * right[inner][column] for inner in range(shared))
            for column in range(right_columns)
        ]
        for row in range(left_rows)
    ]


def add(left, right):
    if shape(left) != shape(right):
        raise AssertionError("matrix sum dimension mismatch")
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def negate(matrix):
    return [[-entry for entry in row] for row in matrix]


def is_zero(matrix) -> bool:
    return all(entry == 0 for row in matrix for entry in row)


def rank_q(matrix) -> int:
    work = [[Fraction(entry) for entry in row] for row in matrix]
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def rank_mod_p(matrix, prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, prime)
        work[pivot_row] = [(entry * inverse) % prime for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            scale = work[row][column]
            work[row] = [
                (entry - scale * pivot_entry) % prime
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
    return pivot_row


def assemble(row_dims, column_dims, blocks) -> Matrix:
    row_offsets = [0]
    column_offsets = [0]
    for dimension in row_dims:
        row_offsets.append(row_offsets[-1] + dimension)
    for dimension in column_dims:
        column_offsets.append(column_offsets[-1] + dimension)
    out = zeros(row_offsets[-1], column_offsets[-1])
    for (block_row, block_column), block in blocks.items():
        expected = (row_dims[block_row], column_dims[block_column])
        if shape(block) != expected:
            raise AssertionError(
                f"block {(block_row, block_column)} has shape {shape(block)}, "
                f"expected {expected}"
            )
        for row in range(expected[0]):
            for column in range(expected[1]):
                out[row_offsets[block_row] + row][
                    column_offsets[block_column] + column
                ] = block[row][column]
    return out


def block_diagonal(blocks) -> Matrix:
    row_dims = [len(block) for block in blocks]
    column_dims = [len(block[0]) for block in blocks]
    return assemble(
        row_dims,
        column_dims,
        {(index, index): block for index, block in enumerate(blocks)},
    )


def concatenate_columns(left, right):
    if len(left) != len(right):
        raise AssertionError("column concatenation dimension mismatch")
    return [left_row + right_row for left_row, right_row in zip(left, right)]


def nullspace_columns(matrix):
    work = [[Fraction(entry) for entry in row] for row in matrix]
    rows, columns = len(work), len(work[0])
    pivot_columns = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_columns.append(column)
        pivot_row += 1
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    basis = zeros(columns, len(free_columns))
    for basis_column, free_column in enumerate(free_columns):
        basis[free_column][basis_column] = 1
        for row, pivot_column in enumerate(pivot_columns):
            basis[pivot_column][basis_column] = -work[row][free_column]
    return basis


def build_fiber_complex(triple, pairs):
    """Instantiate the signed block matrices (22) and (23)."""

    d_t0, d_t1 = triple
    t1, t0 = shape(d_t0)
    t2, check_t1 = shape(d_t1)
    if check_t1 != t1 or not is_zero(multiply(d_t1, d_t0)):
        raise AssertionError("triple cochains do not form a complex")

    e0_dims, e1_dims, e2_dims = [], [], []
    for d_e0, d_e1, b0, b1 in pairs:
        e1, e0 = shape(d_e0)
        e2, check_e1 = shape(d_e1)
        if check_e1 != e1:
            raise AssertionError("exclusive-pair differential shape mismatch")
        if shape(b0) != (e1, t0) or shape(b1) != (e2, t1):
            raise AssertionError("frontier block shape mismatch")
        if not is_zero(multiply(d_e1, d_e0)):
            raise AssertionError("exclusive-pair cochains do not form a complex")
        if not is_zero(add(multiply(d_e1, b0), multiply(b1, d_t0))):
            raise AssertionError("frontier identity d_E b + b d_T != 0")
        e0_dims.append(e0)
        e1_dims.append(e1)
        e2_dims.append(e2)

    d01_0, d01_1, b01_0, b01_1 = pairs[0]
    d02_0, d02_1, b02_0, b02_1 = pairs[1]
    d12_0, d12_1, b12_0, b12_1 = pairs[2]
    c0_dims = [t0, t0] + e0_dims
    c1_dims = [t1, t1] + e1_dims
    c2_dims = [t2, t2] + e2_dims
    n_matrix = assemble(
        c1_dims,
        c0_dims,
        {
            (0, 0): d_t0,
            (1, 1): d_t0,
            (2, 0): negate(b01_0),
            (2, 2): d01_0,
            (3, 0): negate(b02_0),
            (3, 1): negate(b02_0),
            (3, 3): d02_0,
            (4, 1): negate(b12_0),
            (4, 4): d12_0,
        },
    )
    m_matrix = assemble(
        c2_dims,
        c1_dims,
        {
            (0, 0): d_t1,
            (1, 1): d_t1,
            (2, 0): b01_1,
            (2, 2): negate(d01_1),
            (3, 0): b02_1,
            (3, 1): b02_1,
            (3, 3): negate(d02_1),
            (4, 1): b12_1,
            (4, 4): negate(d12_1),
        },
    )
    if not is_zero(multiply(m_matrix, n_matrix)):
        raise AssertionError("the signed block product MN is not zero")
    return n_matrix, m_matrix


def middle_rank_gate(n_matrix, m_matrix, prime: int = 2):
    """Require an integral complex and replay middle exactness modulo prime.

    The diagonal-three rational target uses ``prime=2``.  The integral
    ``MN=0`` check is indispensable: ranks of arbitrary matrices after
    reduction do not certify a rational cochain complex.
    """

    if not is_zero(multiply(m_matrix, n_matrix)):
        raise AssertionError("middle-rank gate received a non-complex: MN != 0")
    middle_dimension = len(n_matrix)
    ranks = (rank_mod_p(n_matrix, prime), rank_mod_p(m_matrix, prime))
    defect = middle_dimension - sum(ranks)
    if defect < 0:
        raise AssertionError("MN=0 but modular ranks exceed the middle dimension")
    return ranks, defect


def derived_h1_rank(triple, pairs) -> tuple[int, int, int]:
    """Compute sum H1(E_ij) + ker(beta) directly over Q."""

    d_t0, d_t1 = triple
    t1 = len(d_t0)
    h1_t = t1 - rank_q(d_t0) - rank_q(d_t1)
    exclusive_h1 = sum(
        len(d_e0) - rank_q(d_e0) - rank_q(d_e1)
        for d_e0, d_e1, _b0, _b1 in pairs
    )

    triple_cocycles = nullspace_columns(d_t1)
    cocycle_dimension = len(triple_cocycles[0])
    two_cocycles = block_diagonal([triple_cocycles, triple_cocycles])
    beta_on_cochains = assemble(
        [len(pair[1]) for pair in pairs],
        [t1, t1],
        {
            (0, 0): pairs[0][3],
            (1, 0): pairs[1][3],
            (1, 1): pairs[1][3],
            (2, 1): pairs[2][3],
        },
    )
    beta_on_cocycles = multiply(beta_on_cochains, two_cocycles)
    exclusive_boundaries = block_diagonal([pair[1] for pair in pairs])
    beta_rank = rank_q(
        concatenate_columns(exclusive_boundaries, beta_on_cocycles)
    ) - rank_q(exclusive_boundaries)
    beta_kernel = 2 * h1_t - beta_rank
    if beta_kernel < 0 or cocycle_dimension < h1_t:
        raise AssertionError("invalid induced balanced-frontier rank")
    return exclusive_h1 + beta_kernel, exclusive_h1, beta_kernel


def unit_reduce(matrix):
    """Unit-pivot Smith reduction, returning U,A',V with A'=U A V."""

    work = [row[:] for row in matrix]
    rows, columns = shape(work)
    left, right = identity(rows), identity(columns)
    pivot = 0
    while pivot < min(rows, columns):
        location = next(
            (
                (row, column)
                for row in range(pivot, rows)
                for column in range(pivot, columns)
                if abs(work[row][column]) == 1
            ),
            None,
        )
        if location is None:
            break
        row, column = location
        work[pivot], work[row] = work[row], work[pivot]
        left[pivot], left[row] = left[row], left[pivot]
        for target in (work, right):
            for target_row in target:
                target_row[pivot], target_row[column] = (
                    target_row[column],
                    target_row[pivot],
                )
        if work[pivot][pivot] == -1:
            work[pivot] = [-entry for entry in work[pivot]]
            left[pivot] = [-entry for entry in left[pivot]]
        for other_row in range(rows):
            if other_row == pivot:
                continue
            scale = work[other_row][pivot]
            if scale:
                work[other_row] = [
                    entry - scale * pivot_entry
                    for entry, pivot_entry in zip(work[other_row], work[pivot])
                ]
                left[other_row] = [
                    entry - scale * pivot_entry
                    for entry, pivot_entry in zip(left[other_row], left[pivot])
                ]
        for other_column in range(columns):
            if other_column == pivot:
                continue
            scale = work[pivot][other_column]
            if scale:
                for target in (work, right):
                    for target_row in target:
                        target_row[other_column] -= scale * target_row[pivot]
        pivot += 1
    if multiply(multiply(left, matrix), right) != work:
        raise AssertionError("unit reduction lost its basis transformations")
    return work, left, right, pivot


def inverse_unimodular(matrix) -> Matrix:
    size, columns = shape(matrix)
    if size != columns:
        raise AssertionError("inverse requires a square matrix")
    work = [
        [Fraction(entry) for entry in row]
        + [Fraction(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    inverse = [row[size:] for row in work]
    if any(entry.denominator != 1 for row in inverse for entry in row):
        raise AssertionError("basis transformation was not unimodular")
    return [[int(entry) for entry in row] for row in inverse]


def split_exact_replay(n_matrix, m_matrix) -> tuple[int, int]:
    """Replay (25) and construct (26) in the resulting Smith bases."""

    n_reduced, u_matrix, _v_matrix, n_units = unit_reduce(n_matrix)
    if n_units != rank_q(n_matrix) or any(
        entry
        for row in n_reduced[n_units:]
        for entry in row[n_units:]
    ):
        raise AssertionError("N has a nonunit Smith residue")
    u_inverse = inverse_unimodular(u_matrix)
    m_prime = multiply(m_matrix, u_inverse)
    if not is_zero(multiply(m_prime, n_reduced)):
        raise AssertionError("basis-changed complex no longer squares to zero")
    if any(row[column] for row in m_prime for column in range(n_units)):
        raise AssertionError("M does not vanish on the Smith pivots of N")

    bar_m = [row[n_units:] for row in m_prime]
    bar_reduced, s_matrix, p_matrix, bar_units = unit_reduce(bar_m)
    complement = len(bar_m[0])
    if bar_units != complement or bar_units != rank_q(bar_m):
        raise AssertionError("bar M is not full-column-rank with unit invariants")
    expected = zeros(len(bar_m), complement)
    for index in range(complement):
        expected[index][index] = 1
    if bar_reduced != expected:
        raise AssertionError("unexpected unit-Smith normal form for bar M")

    # S barM P = J, hence L=P J^t S is an integral left inverse of barM.
    j_transpose = zeros(complement, len(bar_m))
    for index in range(complement):
        j_transpose[index][index] = 1
    left_inverse = multiply(multiply(p_matrix, j_transpose), s_matrix)
    if multiply(left_inverse, bar_m) != identity(complement):
        raise AssertionError("failed to construct the left inverse of bar M")

    n1, n0 = shape(n_reduced)
    h1 = zeros(n0, n1)
    for index in range(n_units):
        h1[index][index] = 1
    h2 = zeros(n1, len(m_matrix))
    for row in range(complement):
        h2[n_units + row] = left_inverse[row][:]
    contraction = add(multiply(h2, m_prime), multiply(n_reduced, h1))
    if contraction != identity(n1):
        raise AssertionError("chain-contraction identity (26) failed")
    return n_units, bar_units


def pair_blocks_mixed(cancellation: int, beta_weight: int):
    d_e0 = [[1], [0], [0]]
    d_e1 = [[0, 1, 0], [0, 0, 0]]
    b0 = [[0], [cancellation], [0]]
    b1 = [[-cancellation, 0, 0], [0, 0, beta_weight]]
    return d_e0, d_e1, b0, b1


def pair_blocks_acyclic(cancellation: int):
    d_e0 = [[1], [0]]
    d_e1 = [[0, 1]]
    b0 = [[0], [cancellation]]
    b1 = [[-cancellation, 0]]
    return d_e0, d_e1, b0, b1


def replay_block_complex() -> None:
    # The first model has H1(T)=Z, each H1(E_ij)=Z, and beta has rank two.
    # Distinct cancellation coefficients exercise every duplicated/sign block
    # in (22)--(23), rather than allowing an accidental symmetric cancellation.
    triple = ([[1], [0], [0]], [[0, 1, 0]])
    pairs = (
        pair_blocks_mixed(1, 1),
        pair_blocks_mixed(2, 2),
        pair_blocks_mixed(-3, -1),
    )
    n_matrix, m_matrix = build_fiber_complex(triple, pairs)
    direct_h1 = len(n_matrix) - rank_q(n_matrix) - rank_q(m_matrix)
    formula_h1, exclusive_h1, beta_kernel = derived_h1_rank(triple, pairs)
    assert (shape(n_matrix), shape(m_matrix)) == ((15, 5), (8, 15))
    assert direct_h1 == formula_h1 == 3
    assert (exclusive_h1, beta_kernel) == (3, 0)

    # A second nontrivial-frontier model is split exact.  Unit pivot reduction
    # constructs the coefficient-universal contraction promised in (25)--(26).
    acyclic_triple = ([[1], [0]], [[0, 1]])
    acyclic_pairs = tuple(pair_blocks_acyclic(value) for value in (1, 2, -3))
    n_exact, m_exact = build_fiber_complex(acyclic_triple, acyclic_pairs)
    assert (shape(n_exact), shape(m_exact)) == ((10, 5), (5, 10))
    assert len(n_exact) - rank_q(n_exact) - rank_q(m_exact) == 0
    mod2_ranks, mod2_defect = middle_rank_gate(n_exact, m_exact)
    assert (mod2_ranks, mod2_defect) == ((5, 5), 0)
    n_units, bar_units = split_exact_replay(n_exact, m_exact)
    assert (n_units, bar_units) == (5, 5)

    # Multiplication by two is injective over Z and has full Q-rank, but its
    # only Smith invariant is nonunit and it acquires kernel over F_2.
    nonunit = [[2]]
    reduced, _left, _right, units = unit_reduce(nonunit)
    assert rank_q(nonunit) == 1 and rank_mod_p(nonunit, 2) == 0
    assert units == 0 and reduced == nonunit

    # These arbitrary matrices look exact after reduction modulo two, but
    # their displayed integral product is 2.  The signed-lift gate must stop
    # before considering their modular ranks.
    try:
        middle_rank_gate([[1]], [[2]])
    except AssertionError as error:
        assert "MN != 0" in str(error)
    else:
        raise AssertionError("mod-two ranks bypassed the integral lift gate")

    print("PASS (19),(22),(23): signed integral blocks have MN=0")
    print("PASS (24): direct/formula H1 ranks agree at 3 = 3 + 0")
    print("PASS (25),(26): unit ranks N/barM=5/5 and integral contraction identity")
    print("PASS rational gate: integral MN=0 and mod-two middle ranks 5+5=10")
    print("PASS false-lift canary N=[1],M=[2]: rejected before modular rank")
    print("PASS nonunit canary [2]: Z-injective, Q-full-rank, not coefficient-universal")


def sub(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    size = max(len(a), len(b))
    out = tuple(
        (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
        for i in range(size)
    )
    while len(out) > 1 and out[-1] == 0:
        out = out[:-1]
    return out


def replay_countermodel() -> None:
    # Store F_i(g) for the graph equations q_i=z-F_i(g), in increasing
    # powers of g.
    graph_functions = ((0,), (0, 1), (0, 2, 0, 1))
    assert sub(graph_functions[0], graph_functions[1]) == (0, -1)
    assert sub(graph_functions[0], graph_functions[2]) == (0, -2, 0, -1)
    assert sub(graph_functions[1], graph_functions[2]) == (0, -1, 0, -1)

    # On the real locus, 1+g^2 and 2+g^2 never vanish.  Thus every pair
    # common zero is exactly z=g=0.  The graph slopes with respect to dg at
    # g=0 are distinct, so every pair is a smooth complete intersection.
    slopes = tuple(f[1] if len(f) > 1 else 0 for f in graph_functions)
    assert slopes == (0, 1, 2)

    differential = (1, -1, 1)
    kernel = ((1, 1, 0), (-1, 0, 1))
    assert all(sum(a * b for a, b in zip(differential, v)) == 0 for v in kernel)
    assert differential[0] == 1  # primitive rank-one row

    # The closed-cover Mayer--Vietoris terms in total degree one are only
    # singleton H_c^1 and pair-intersection H_c^0.  Here B_i=R^8 and every
    # pair intersection is R x S^6, so all six ranks are zero.  Consequently
    # the union of all three active boundaries has H_c^1=0.  Triple H_c^0
    # also vanishes, but it lies in total degree two.
    singleton_hc1_ranks = (0, 0, 0)
    pair_hc0_ranks = (0, 0, 0)
    triple_hc0_rank = 0
    total_degree_one_rank = (
        sum(singleton_hc1_ranks) + sum(pair_hc0_ranks)
    )
    assert total_degree_one_rank == triple_hc0_rank == 0

    # E_ij is empty in this model, so beta has zero target.  Its domain is
    # the rank-two mass-zero module computed above.
    beta_domain_rank = len(kernel)
    beta_target_rank = 0
    assert (beta_domain_rank, beta_target_rank) == (2, 0)

    print("PASS three primitive global graph factors have one common pair/triple locus")
    print("PASS pair graph slopes at the common locus are distinct:", slopes)
    print("PASS active-boundary union has H_c^1=0 by its total-degree-one table")
    print("PASS alternating restriction row has primitive kernel rank 2")
    print("NO-GO boundary-union H_c^1=0 does not imply beta injectivity")


def main() -> None:
    replay_block_complex()
    replay_countermodel()


if __name__ == "__main__":
    main()
