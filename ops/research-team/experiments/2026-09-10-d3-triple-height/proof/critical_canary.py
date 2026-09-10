"""Exact replay of the inherited simultaneous (39,48,50) critical point."""
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
Y = sp.Matrix([
    [1, 0, 0, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 1, -1, 4, 7],
    [0, 0, 1, 0, 1, 2, -5, -4],
    [0, 0, 0, 1, 1, 3, 2, 5],
])
supports = {
    "P48": ("123", "145", "246", "356"),
    "Q39_ordinary": ("125", "126", "356", "378"),
    "R50": ("123", "145", "246", "378"),
}


def normal(edge):
    cols = Y[:, [int(j) - 1 for j in edge]]
    return sp.Matrix([
        (-1) ** (3 + j) * cols[[k for k in range(4) if k != j], :].det()
        for j in range(4)
    ])


brackets = {
    "".join(str(j + 1) for j in I): Y[:, I].det()
    for I in itertools.combinations(range(8), 4)
}
assert all(brackets.values())
records = {}
raw = {}
for name, support in supports.items():
    N = sp.Matrix.vstack(*(normal(edge).T for edge in support))
    assert N.rank() == 3 and N.det() == 0
    assert all(N[list(I), :].rank() == 3 for I in itertools.combinations(range(4), 3))
    q = N.nullspace()[0]
    lam = N.T.nullspace()[0]
    assert all(lam)
    raw[name] = N, q, lam
    records[name] = {
        "support": support,
        "normals": [[str(v) for v in row] for row in N.tolist()],
        "rank": N.rank(),
        "concurrence": [str(v) for v in q],
        "circuit_dependence": [str(v) for v in lam],
    }

p = raw["P48"][1]
gammas = []
for name in ("Q39_ordinary", "R50"):
    N, q, lam = raw[name]
    gamma = sp.zeros(1, 8)
    for coefficient, edge in zip(lam, supports[name]):
        labels = [int(j) - 1 for j in edge]
        for slot, j in enumerate(labels):
            cols = [Y[:, k] for k in labels]
            cols[slot] = p
            gamma[j] += coefficient * sp.Matrix.hstack(*cols, q).det()
    records[name]["vertical_gradient_in_eight_heights"] = [str(v) for v in gamma]
    gammas.append(gamma)
G = sp.Matrix.vstack(*gammas)
assert G.rank() == 0
assert gammas[1] == sp.zeros(1, 8)
assert raw["P48"][1] == raw["R50"][1]
assert sp.Matrix.hstack(*(raw[n][1] for n in supports)).rank() == 2

a, b, c, d, e, f, g, h, i = sp.symbols("a b c d e f g h i")
q39 = a*f-a*i-c*d*i+c*f*g-c*f+c*i+d*i-f*g
q48 = a+b*c-b-c
q50 = b*f-b*i+d*i-f*g
assert sp.expand(q39-(f-i)*q48-(1-c)*q50) == 0

result = {
    "scope": "One inherited simultaneous critical canary; no new triple coverage",
    "parent_matrix": [[str(v) for v in row] for row in Y.tolist()],
    "parent_brackets": {k: str(v) for k, v in brackets.items()},
    "all_70_parent_brackets_nonzero": True,
    "ordinary_occurrences": records,
    "vertical_gradient_rank": G.rank(),
    "concurrence_span_rank": 2,
    "P_R_concurrence_equal": True,
    "global_polynomial_identity": "q39=(f-i)*q48+(1-c)*q50",
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
(ROOT / "CRITICAL_CANARY.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS: uniform simultaneous critical point has p=r and vertical rank0")
print("PASS: q39=(f-i)*q48+(1-c)*q50; the full triple zero set equals a pair")
