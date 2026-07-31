import json
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction
import sympy as sp

def get_exact_farkas(U_frac, sig, ch_classes, n=5, k=3):
    # U_frac is 5x3 list of Fractions
    # We want to show the system w_t >= 1, sig_ci * W_ij >= 0 is infeasible.
    # W_ij = sum_{t!=i,j} s_t w_t |D_tij| / ||u_i x u_j||
    # To clear denominators, we can define modified weights and use |D_tij| directly.
    # Actually, sig_ci * sum_{t!=i,j} s_t w_t |D_tij| >= 0 is equivalent since ||u_i x u_j|| > 0.
    
    # Precompute exact absolute determinants
    D = {}
    for i in range(n):
        for j in range(i+1, n):
            for t in range(n):
                if t == i or t == j:
                    continue
                # Det(u_t, u_i, u_j)
                det = U_frac[t][0]*(U_frac[i][1]*U_frac[j][2] - U_frac[i][2]*U_frac[j][1]) - \
                      U_frac[t][1]*(U_frac[i][0]*U_frac[j][2] - U_frac[i][2]*U_frac[j][0]) + \
                      U_frac[t][2]*(U_frac[i][0]*U_frac[j][1] - U_frac[i][1]*U_frac[j][0])
                D[(t, i, j)] = abs(det)
                
    classes = []
    for i in range(n):
        for j in range(i+1, n):
            classes.append((i, j))
            
    # We want to solve a float LP first to find the Farkas multipliers, then rationalise them
    # Constraints: sum_{t} (sig_ci * s_t * |D_tij|) w_t >= 0
    # w_t >= 1 (so -w_t <= -1)
    
    A_ub = []
    b_ub = []
    
    # We want to find y_ci >= 0 such that sum_ci y_ci (sig_ci * s_t * |D_tij|) <= -1 for all t
    # Wait, Farkas on A w >= b, w >= 0. We have w >= 1.
    # Let w = 1 + x, x >= 0.
    # sig_ci * W_ij >= 0  => sig_ci * sum s_t (1+x_t) |D_tij| >= 0
    # => sum_t (sig_ci s_t |D_tij|) x_t >= - sum_t (sig_ci s_t |D_tij|)
    
    # Let's just use linprog to find if w >= 1, A w >= 0 is feasible.
    A_float = []
    b_float = []
    A_exact = []
    for ci, (i, j) in enumerate(classes):
        row_exact = []
        row_float = []
        for t in range(n):
            if t == i or t == j:
                row_exact.append(Fraction(0))
                row_float.append(0.0)
            else:
                s_t = 1 if t < k else -1
                val = sig[ci] * s_t * D[(t, i, j)]
                row_exact.append(val)
                row_float.append(float(val))
        A_exact.append(row_exact)
        A_float.append(row_float)
        
    A_float = np.array(A_float)
    
    # LP: min 0, subject to A w >= 0, w >= 1.
    # A w >= 0 => -A w <= 0
    res = linprog(c=np.zeros(n), A_ub=-A_float, b_ub=np.zeros(len(classes)), bounds=[(1, None)]*n, method="highs")
    
    if res.status == 0:
        return None # Feasible, no Farkas certificate
    
    # If infeasible, dual is unbounded.
    # Dual: max sum(0) + sum y_i (0) + sum z_t (1). wait.
    # Find y >= 0 such that y^T A <= -1
    # LP for dual: min sum(y), y^T A <= -1, y >= 0
    res_dual = linprog(c=np.ones(len(classes)), A_ub=A_float.T, b_ub=-np.ones(n), bounds=[(0, None)]*len(classes), method="highs")
    
    if res_dual.status == 0:
        y_float = res_dual.x
        # Rationalize y
        y_exact = [Fraction(y).limit_denominator(1000) for y in y_float]
        return [str(y) for y in y_exact]
    return None

def main():
    rng = np.random.default_rng(42)
    U_float = rng.normal(size=(5, 3))
    U_float /= np.linalg.norm(U_float, axis=1, keepdims=True)
    
    U_frac = []
    for i in range(5):
        row = []
        for j in range(3):
            f = Fraction(U_float[i, j]).limit_denominator(10)
            row.append(f)
        U_frac.append(row)
        
    U = np.array([[float(x) for x in row] for row in U_frac])
    n = 5
    classes = []
    for i in range(n):
        for j in range(i + 1, n):
            r = np.cross(U[i], U[j])
            r = r / np.linalg.norm(r)
            classes.append((i, j, r))
            
    dirs = [c[2] + rng.normal(scale=1e-4, size=3) for c in classes for _ in range(8)]
    dirs += [-d for d in dirs] + list(rng.normal(size=(6 * n * n, 3)))
    cham = {}
    for c in dirs:
        d = U @ c
        if np.all(np.abs(d) > 1e-9):
            cham[tuple(np.sign(d).astype(int))] = True
    chambers = [np.array(e) for e in cham]
    
    ch_classes = []
    for eps in chambers:
        lst = []
        for ci, (i, j, r) in enumerate(classes):
            d = eps * (U @ r)
            mask = np.ones(n, bool)
            mask[[i, j]] = False
            if np.all(d[mask] > 1e-9) or np.all(d[mask] < -1e-9):
                lst.append(ci)
        ch_classes.append(lst)
        
    farkas_results = {}
    for bits in range(1024):
        sig = [(1 if (bits & (1 << ci)) else -1) for ci in range(10)]
        ok = True
        for lst in ch_classes:
            vals = [sig[ci] for ci in lst]
            if len(set(vals)) < 2:
                ok = False
                break
        if ok:
            # Solve exact LP
            cert = get_exact_farkas(U_frac, sig, ch_classes, n=5, k=3)
            farkas_results[bits] = cert
            
    with open("farkas_t0.json", "w") as f:
        json.dump(farkas_results, f, indent=2)

if __name__ == "__main__":
    main()
