"""Independent original-determinant replay of the referee's rank11 canary."""
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
rat = sp.Rational
t = list(map(sp.Integer, range(7))) + [rat(485, 173)]
a = [0, 0, rat(-19203,1946), rat(7785,973), rat(13840,973),
     rat(12975,973), rat(1730,139), rat(624,139)]
b = [0, 0, 0, rat(-12975,973), rat(-17300,973), rat(-25950,973),
     rat(692,139), 1]
Y = sp.Matrix([sp.ones(1, 8).tolist()[0], t, a, b])
supports = {
    "P": ("123", "145", "246", "378"),
    "Q": ("146", "278", "348", "567"),
    "R": ("156", "178", "245", "368"),
}


def rows(matrix, support):
    out = []
    for edge in support:
        C = matrix[:, [int(i)-1 for i in edge]]
        out.append([
            (-1)**(3+j)*C[[k for k in range(4) if k != j], :].det()
            for j in range(4)
        ])
    return sp.Matrix(out)


brackets = {
    "".join(str(i+1) for i in I): Y[:, I].det()
    for I in itertools.combinations(range(8), 4)
}
assert all(brackets.values())
expected = {"P": sp.Matrix([0,0,1,0]), "Q": sp.Matrix([0,0,0,1]),
            "R": sp.Matrix([0,0,1,1])}
record = {}
for name, edges in supports.items():
    N = rows(Y, edges)
    assert N.rank() == 3 and N*expected[name] == sp.zeros(4, 1)
    assert all(N[list(I), :].rank() == 3 for I in itertools.combinations(range(4), 3))
    record[name] = {"support": edges, "normal_rank": 3,
                    "concurrence": list(map(str, expected[name]))}

# Construct the12-by16 constraint matrix by determinant evaluations, rather
# than importing the producer's sparse-row routine.
variables = sp.symbols("a0:8") + sp.symbols("b0:8")
L = sp.Matrix([sp.ones(1, 8).tolist()[0], t, variables[:8], variables[8:]])
eqs = []
for name, edges in supports.items():
    for edge in edges:
        eqs.append(sp.expand(sp.Matrix.hstack(
            L[:, [int(i)-1 for i in edge]], expected[name]
        ).det()))
M, rhs = sp.linear_eq_to_matrix(eqs, variables)
assert rhs == sp.zeros(12, 1)
assert M.rank() == 11
assert M*sp.Matrix(a+b) == sp.zeros(12, 1)
col_pivots = list(M.rref()[1])
row_pivots = list(M[:, col_pivots].T.rref()[1])
minor = M[row_pivots, col_pivots].det()
assert minor != 0

# Each parent occurs at most twice in every selected occurrence, so the
# occurrence determinant under a one-parent displacement is degree at most2.
# This symmetric finite difference is therefore the exact derivative.
gradients = []
for name in ("Q", "R"):
    gamma = []
    for j in range(8):
        plus, minus = Y.copy(), Y.copy()
        plus[2, j] += 1
        minus[2, j] -= 1
        gamma.append((rows(plus, supports[name]).det()-
                      rows(minus, supports[name]).det())/2)
    gradients.append(gamma)
G = sp.Matrix(gradients)
assert G.rank() == 2
for gauge in (sp.ones(8, 1), sp.Matrix(t), sp.Matrix(a), sp.Matrix(b)):
    assert G*gauge == sp.zeros(2, 1)
rank_minor = None
for I in itertools.combinations(range(8), 2):
    d = G[:, I].det()
    if d:
        rank_minor = {"columns_0based": I, "determinant": str(d)}
        break
assert rank_minor is not None

result = {
    "scope": "Independent replay of one regular distinct-collinear rank11 canary",
    "parent_matrix": [[str(v) for v in row] for row in Y.tolist()],
    "parent_brackets": {k: str(v) for k, v in brackets.items()},
    "all70_parent_brackets_nonzero": True,
    "ordinary_occurrences": record,
    "stack_rank": 11,
    "nonzero11_minor": {"rows_0based": row_pivots,
                         "columns_0based": col_pivots, "determinant": str(minor)},
    "vertical_gradients_direct_finite_difference": [[str(v) for v in row] for row in G.tolist()],
    "vertical_gradient_rank": 2,
    "nonzero_gradient_minor": rank_minor,
    "normalized_fixed_projection_fiber_dimension": 0,
    "critical_point": False,
    "new_source_orbit_credit": 0,
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
(HERE/"COLLINEAR_RANK11_REPLAY.json").write_text(json.dumps(result, indent=2)+"\n")
print("PASS all70 parent brackets; ordinary distinct collinear concurrences")
print("PASS stack rank11; vertical gradient rank2; four gauge annihilations")
