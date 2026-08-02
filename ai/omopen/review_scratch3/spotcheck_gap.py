"""Independent spot-check of the headline gap claim: float64 loses real
completions once entries pass ~2^30, while the exact oracle does not.
Uses det=+1 unimodular transforms, which preserve EVERY bracket sign
exactly (det(UX_B) = det(U)det(X_B) = det(X_B)), so feasibility is unchanged."""
import io, json, os, sys, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OM = os.path.dirname(HERE)
sys.path.insert(0, OM)
import numpy as np, exactlp, weaponA, catalog

geom = catalog.realize_mod().Geom(9, 4)
c = json.loads(io.open(os.path.join(OM, 'data', 'certs_realizable.jsonl'), encoding='utf-8').readline())
Z0 = np.array(c['matrix'], dtype=object)
chi = np.array([1 if ch == '+' else -1 for ch in c['chi']], dtype=np.int64)
rng = random.Random(7)

SEQ = [(0,1),(1,2),(2,3),(3,0)]
def shear(Z, step):
    i, j = SEQ[step % 4]
    U = [[1 if a==b else 0 for b in range(4)] for a in range(4)]
    U[i][j] = 3                                   # det = +1 exactly
    return np.array([[sum(U[a][k]*Z[k][b] for k in range(4)) for b in range(Z.shape[1])]
                     for a in range(4)], dtype=object)
    i, j = rng.sample(range(4), 2)
    U[i][j] = rng.choice([1, -1, 2, -2])          # det = +1 exactly
    return np.array([[sum(U[a][k] * Z[k][b] for k in range(4)) for b in range(Z.shape[1])]
                     for a in range(4)], dtype=object)

print('%-10s %8s %14s %14s' % ('max|entry|', 'p-cases', 'float feasible', 'exact feasible'))
Z = Z0
for step in range(24):
    mx = max(abs(int(v)) for row in Z for v in row)
    if True:
        fl = ex = 0
        for p in range(9):
            A, bs = weaponA.completion_rows(Z, chi, geom, p)
            Ai = [[int(v) for v in row] for row in A]
            x, t = weaponA._lp_interior(A)
            if x is not None and t is not None and t > 0: fl += 1
            if exactlp.exact_feasible(Ai)[0] == 'FEASIBLE': ex += 1
        print('2^%-8.1f %8d %14d %14d' % (np.log2(float(mx)), 9, fl, ex))
        if mx > 2**40: break
    Z = shear(Z, step)
