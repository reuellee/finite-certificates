#!/usr/bin/env python3
"""Build an exact coordinate-path certificate for the row-2599 12/37 stress pair.

The search is numerical, but the emitted certificate is not: every accepted
configuration is rational (stored by integer homogeneous columns), and the
companion verifier checks all determinant signs with Python integers.  Each
path edge changes one column only, so every constrained determinant is affine
on that edge and endpoint positivity certifies the whole open segment.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import realize

CERTIFICATE = HERE / "data" / "ninth_candidate_12_37_path.npz"
SOURCE = HERE / "data" / "seeat_parent2599_upper178.npz"
FORMAT = "ninth-candidate-12-37-coordinate-path-v1"

ENDPOINTS = (12, 37)
SIGNATURES = (
    32577326938880,
    31532828708796544,
    3510916511430656,
    72042742044167295,
    3476291556529680,
    2137481474473987,
    58098186400358399,
    32444182421504,
    68557050812244096,
)
TRIPLES = tuple(sorted(combinations(range(8), 3), key=lambda q: tuple(reversed(q))))
BASES = tuple(sorted(combinations(range(8), 4), key=lambda q: tuple(reversed(q))))


def det(columns):
    return realize._det_py([[int(columns[row, col]) for col in range(4)] for row in range(4)])


def determinant(v, q):
    return realize._det_py([[int(v[row, col]) for col in q] for row in range(4)])


def parent_signs(y):
    return tuple(1 if determinant(y, q) > 0 else -1 for q in BASES)


def constraints(signs):
    out = [(q, sign) for q, sign in zip(BASES, signs)]
    for j, signature in enumerate(SIGNATURES):
        for bit, triple in enumerate(TRIPLES):
            sign = 1 if (signature >> bit) & 1 else -1
            out.append((triple + (8 + j,), sign))
    return tuple(out)


def exact_ok(v, q, sign):
    return sign * determinant(v, q) > 0


def normals(y):
    y = np.asarray(y, dtype=float)
    y = y / np.max(np.abs(y), axis=0, keepdims=True)
    rows = []
    for q in TRIPLES:
        c = y[:, q]
        rows.append(
            [(-1) ** (i + 3) * np.linalg.det(np.delete(c, i, axis=0)) for i in range(4)]
        )
    rows = np.asarray(rows)
    return rows / np.linalg.norm(rows, axis=1)[:, None]


def witness(y, signature, second=None):
    blocks = []
    for parent in (y,) if second is None else (y, second):
        a = normals(parent)
        signs = np.asarray([1 if (signature >> i) & 1 else -1 for i in range(56)])
        blocks.append(a * signs[:, None])
    signed = np.vstack(blocks)
    result = linprog(
        np.r_[np.zeros(4), -1.0],
        A_ub=np.column_stack((-signed, np.ones(len(signed)))),
        b_ub=np.zeros(len(signed)),
        bounds=[(-1, 1)] * 4 + [(0, None)],
        method="highs",
    )
    if not result.success or result.x[4] <= 1e-10:
        raise RuntimeError("no robust common extension witness")
    x = result.x[:4]
    return x / np.linalg.norm(x)


def primitive(vector):
    vector = [int(x) for x in vector]
    divisor = 0
    for x in vector:
        divisor = gcd(divisor, abs(x))
    if divisor > 1:
        vector = [x // divisor for x in vector]
    return np.asarray(vector, dtype=np.int64)


def rational_vector(target, accepts):
    target = np.asarray(target, dtype=float)
    target /= np.max(np.abs(target))
    for denominator in (10**7, 10**9, 10**11, 10**13, 10**15):
        candidate = primitive(np.rint(target * denominator).astype(object))
        if np.max(np.abs(candidate.astype(object))) >= 2**63:
            continue
        if accepts(candidate):
            return candidate
    raise RuntimeError("could not rationalize an interior ray")


def float_value(v, q, sign, replacement=None):
    block = v[:, q].copy()
    if replacement is not None:
        position, vector = replacement
        block[:, position] = vector
    return sign * np.linalg.det(block)


def normalized_state(y):
    y = np.asarray(y, dtype=float)
    z = np.linalg.solve(y[:, :4], y)
    frame = np.sign(np.r_[z[:, 4], z[0, 5:]])
    z = np.diag(frame[:4] / z[:, 4]) @ z
    for j in range(4):
        z[:, j] /= z[j, j]
    for j in range(5, 8):
        z[:, j] *= frame[4 + j - 5] / z[0, j]
    return z[1:, 5:].T.ravel()


def random_chain(initial, cons, steps, seed):
    v = np.asarray(initial, dtype=float).copy()
    v /= np.linalg.norm(v, axis=0, keepdims=True)
    rng = np.random.default_rng(seed)
    relevant = [[] for _ in range(v.shape[1])]
    for q, sign in cons:
        for position, k in enumerate(q):
            relevant[k].append((q, sign, position))
    updates = []
    samples = []
    for step in range(steps):
        k = int(rng.integers(v.shape[1]))
        x = v[:, k] / np.linalg.norm(v[:, k])
        direction = rng.normal(size=4)
        direction -= x * np.dot(x, direction)
        direction /= np.linalg.norm(direction)
        lo, hi = -np.inf, np.inf
        for q, sign, position in relevant[k]:
            value = float_value(v, q, sign)
            slope = float_value(v, q, sign, (position, direction))
            if value <= 0:
                raise RuntimeError("numerical chain lost feasibility")
            if slope > 1e-14:
                lo = max(lo, -value / slope)
            elif slope < -1e-14:
                hi = min(hi, -value / slope)
        lo = -1.0 if not np.isfinite(lo) else 0.8 * lo
        hi = 1.0 if not np.isfinite(hi) else 0.8 * hi
        t = rng.uniform(lo, hi)
        for _ in range(30):
            candidate = x + t * direction
            candidate /= np.linalg.norm(candidate)
            v[:, k] = candidate
            if min(float_value(v, q, sign) for q, sign, _ in relevant[k]) > 0:
                break
            t *= 0.5
        else:
            raise RuntimeError("coordinate step could not stay interior")
        updates.append((k, candidate.copy()))
        if step % 100 == 0:
            samples.append((step + 1, normalized_state(v[:, :8]), v.copy()))
    return updates, samples


def initial_integer_config(parent, cons):
    parent = np.asarray(parent, dtype=np.int64)
    v = np.zeros((4, 17), dtype=np.int64)
    v[:, :8] = parent
    for j, signature in enumerate(SIGNATURES):
        target = witness(parent, signature)
        k = 8 + j
        relevant = [(q, sign) for q, sign in cons if k in q]
        v[:, k] = rational_vector(
            target,
            lambda candidate, k=k, relevant=relevant: all(
                exact_ok(np.column_stack((v[:, :k], candidate, v[:, k + 1 :])), q, sign)
                for q, sign in relevant
            ),
        )
    if not all(exact_ok(v, q, sign) for q, sign in cons):
        raise RuntimeError("bad exact initial incidence")
    return v


def replay_rational(initial, float_updates, cons):
    v = np.asarray(initial, dtype=np.int64).copy()
    relevant = [[] for _ in range(v.shape[1])]
    for q, sign in cons:
        for k in q:
            relevant[k].append((q, sign))
    columns = []
    vectors = []
    for index, (k, target) in enumerate(float_updates, 1):
        old = v[:, k].copy()

        def accepts(candidate):
            v[:, k] = candidate
            ok = all(exact_ok(v, q, sign) for q, sign in relevant[k])
            v[:, k] = old
            return ok

        candidate = rational_vector(target, accepts)
        v[:, k] = candidate
        columns.append(k)
        vectors.append(candidate.copy())
        if index % 1000 == 0:
            print("  rational replay", index, flush=True)
    return v, np.asarray(columns, dtype=np.uint8), np.asarray(vectors, dtype=np.int64)


def fraction_inverse(matrix):
    n = len(matrix)
    a = [
        [Fraction(int(matrix[i][j])) for j in range(n)]
        + [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    for col in range(n):
        pivot = next(row for row in range(col, n) if a[row][col])
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x / scale for x in a[col]]
        for row in range(n):
            if row == col:
                continue
            scale = a[row][col]
            if scale:
                a[row] = [x - scale * y for x, y in zip(a[row], a[col])]
    return [row[n:] for row in a]


def matmul(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def fraction_column_to_int(column):
    denominator = 1
    for value in column:
        denominator = lcm(denominator, value.denominator)
    integers = [value.numerator * (denominator // value.denominator) for value in column]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    return [value // max(divisor, 1) for value in integers]


def canonicalize(v):
    raw = [[Fraction(int(v[i, j])) for j in range(v.shape[1])] for i in range(4)]
    basis = [[raw[i][j] for j in range(4)] for i in range(4)]
    inverse = fraction_inverse(basis)
    z = matmul(inverse, raw)
    frame = [1 if z[i][4] > 0 else -1 for i in range(4)]
    diagonal = [Fraction(frame[i], 1) / z[i][4] for i in range(4)]
    z = [[diagonal[i] * value for value in z[i]] for i in range(4)]
    for j in range(4):
        scale = Fraction(1, 1) / z[j][j]
        for i in range(4):
            z[i][j] *= scale
    for j in range(5, 8):
        target = 1 if z[0][j] > 0 else -1
        scale = Fraction(target, 1) / z[0][j]
        for i in range(4):
            z[i][j] *= scale
    for j in range(8, 17):
        first = next(z[i][j] for i in range(4) if z[i][j])
        scale = Fraction(1, 1) / abs(first)
        for i in range(4):
            z[i][j] *= scale
    out = [[0] * 17 for _ in range(4)]
    for j in range(17):
        column = fraction_column_to_int([z[i][j] for i in range(4)])
        for i in range(4):
            out[i][j] = column[i]
    return out


def projectively_equal(left, right):
    for j in range(len(left[0])):
        a = [int(left[i][j]) for i in range(4)]
        b = [int(right[i][j]) for i in range(4)]
        scale_sign = None
        for x, y in zip(a, b):
            if x and y:
                scale_sign = x * y
                break
        if scale_sign is None or scale_sign <= 0:
            return False
        if any(a[i] * b[k] != a[k] * b[i] for i in range(4) for k in range(4)):
            return False
    return True


def bridge(canonical_a, canonical_b, cons, subdivisions=100):
    a = np.asarray(canonical_a, dtype=object)
    b = np.asarray(canonical_b, dtype=object)
    if not projectively_equal(canonical_a[:, :5], canonical_b[:, :5]):
        raise RuntimeError("canonical projective frames disagree")
    # Replace the first five columns by A's positive representatives.  Give
    # each of the remaining parent columns the same first coordinate at the
    # two endpoints; these are positive column rescalings, so they do not
    # change either projective endpoint.
    b[:, :5] = a[:, :5]
    parent_a = a[:, :8].copy()
    parent_b = b[:, :8].copy()
    for j in (5, 6, 7):
        if int(parent_a[0, j]) * int(parent_b[0, j]) <= 0:
            raise RuntimeError("canonical affine signs disagree")
        old_a = parent_a[:, j].copy()
        old_b = parent_b[:, j].copy()
        parent_a[:, j] = old_a * abs(int(old_b[0]))
        parent_b[:, j] = old_b * abs(int(old_a[0]))
        if int(parent_a[0, j]) != int(parent_b[0, j]):
            raise RuntimeError("failed to align affine representatives")
    v = a.copy()
    v[:, :8] = parent_a
    bridge_start = v.copy()
    columns, vectors = [], []
    for step in range(subdivisions):
        next_full_parent = parent_a.copy()
        for parent_column in (5, 6, 7):
            next_full_parent[:, parent_column] = (
                (subdivisions - step - 1) * parent_a[:, parent_column]
                + (step + 1) * parent_b[:, parent_column]
            )
        for parent_column in (5, 6, 7):
            next_parent = v[:, :8].copy()
            next_parent[:, parent_column] = next_full_parent[:, parent_column]
            if parent_signs(np.asarray(next_parent, dtype=object)) != parent_signs(np.asarray(v[:, :8], dtype=object)):
                raise RuntimeError("subdivided canonical bridge leaves parent cell")
            for j, signature in enumerate(SIGNATURES):
                target = witness(v[:, :8], signature, next_parent)
                k = 8 + j

                def accepts(candidate, k=k, signature=signature):
                    for parent in (v[:, :8], next_parent):
                        trial = np.column_stack((parent, candidate))
                        for bit, triple in enumerate(TRIPLES):
                            sign = 1 if (signature >> bit) & 1 else -1
                            if sign * determinant(trial, triple + (8,)) <= 0:
                                return False
                    return True

                candidate = rational_vector(target, accepts).astype(object)
                v[:, k] = candidate
                columns.append(k)
                vectors.append(candidate.tolist())
            v[:, parent_column] = next_parent[:, parent_column]
            columns.append(parent_column)
            vectors.append([int(x) for x in next_parent[:, parent_column]])
            if not all(exact_ok(v, q, sign) for q, sign in cons):
                raise RuntimeError("exact bridge endpoint failed")
    for j in range(9):
        k = 8 + j
        v[:, k] = b[:, k]
        columns.append(k)
        vectors.append([int(x) for x in b[:, k]])
        if not all(exact_ok(v, q, sign) for q, sign in cons if k in q):
            raise RuntimeError("could not attach B extension witnesses")
    if not projectively_equal(v.tolist(), b.tolist()):
        raise RuntimeError("bridge does not end at canonical B")
    return bridge_start, columns, vectors


def unicode_array(values):
    strings = np.asarray(values, dtype=str)
    return strings


def main():
    source = np.load(SOURCE, allow_pickle=False)
    parents = [np.asarray(source["chart_matrix"][index], dtype=np.int64) for index in ENDPOINTS]
    signs = parent_signs(parents[0])
    if parent_signs(parents[1]) != signs:
        raise RuntimeError("endpoint parents differ")
    cons = constraints(signs)
    initial = [initial_integer_config(parent, cons) for parent in parents]
    print("exact initial incidences ready", flush=True)
    chains = [random_chain(v, cons, 12_000, seed) for v, seed in zip(initial, (91, 104))]
    best = (float("inf"), None, None)
    samples_a, samples_b = chains[0][1], chains[1][1]
    all_states = np.vstack([sample[1] for sample in samples_a + samples_b])
    scale = np.median(np.abs(all_states - np.median(all_states, axis=0)), axis=0)
    scale[scale < 1e-8] = 1
    qa = np.asarray([np.arcsinh(sample[1] / scale) for sample in samples_a])
    qb = np.asarray([np.arcsinh(sample[1] / scale) for sample in samples_b])
    for i, x in enumerate(qa):
        distances = np.sum((qb - x) ** 2, axis=1)
        j = int(np.argmin(distances))
        if distances[j] < best[0]:
            best = (float(distances[j]), i, j)
    _, ia, ib = best
    count_a, count_b = samples_a[ia][0], samples_b[ib][0]
    print("nearest samples", best, "updates", count_a, count_b, flush=True)
    final_a, col_a, vec_a = replay_rational(initial[0], chains[0][0][:count_a], cons)
    final_b, col_b, vec_b = replay_rational(initial[1], chains[1][0][:count_b], cons)
    canonical_a = np.asarray(canonicalize(final_a), dtype=object)
    canonical_b = np.asarray(canonicalize(final_b), dtype=object)
    if not all(exact_ok(canonical_a, q, sign) for q, sign in cons):
        raise RuntimeError("canonical A failed")
    if not all(exact_ok(canonical_b, q, sign) for q, sign in cons):
        raise RuntimeError("canonical B failed")
    bridge_start, bridge_columns, bridge_vectors = bridge(canonical_a, canonical_b, cons)
    np.savez_compressed(
        CERTIFICATE,
        format=np.asarray(FORMAT),
        parent_index=np.asarray(2599, dtype=np.int64),
        endpoint=np.asarray(ENDPOINTS, dtype=np.uint16),
        signature=np.asarray(SIGNATURES, dtype=np.uint64),
        initial_p_a=initial[0][:, 8:].T,
        initial_p_b=initial[1][:, 8:].T,
        update_col_a=col_a,
        update_vec_a=vec_a,
        update_col_b=col_b,
        update_vec_b=vec_b,
        canonical_a=unicode_array(canonical_a),
        canonical_b=unicode_array(canonical_b),
        bridge_start=unicode_array(bridge_start),
        bridge_col=np.asarray(bridge_columns, dtype=np.uint8),
        bridge_vec=unicode_array(bridge_vectors),
    )
    print("WROTE", CERTIFICATE)
    print("segments", len(col_a), len(bridge_columns), len(col_b))


if __name__ == "__main__":
    main()
