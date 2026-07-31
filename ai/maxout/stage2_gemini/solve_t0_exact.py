import numpy as np
import itertools
from scipy.optimize import linprog
import json
import sympy

def get_U():
    return np.array([
        [ 1,  2,  3],
        [-1,  1,  4],
        [ 2, -3,  1],
        [-3, -1,  2],
        [ 1,  4, -1]
    ])

def build_classes(U):
    n = len(U)
    classes = []
    class_idx = 0
    for i in range(n):
        for j in range(i+1, n):
            r = np.cross(U[i], U[j])
            classes.append((i, j, r, class_idx))
            class_idx += 1
    return classes

def build_chambers(U):
    chambers = []
    np.random.seed(42)
    found = set()
    for _ in range(100000):
        c = np.random.randn(3)
        eps = tuple(np.sign(U @ c).astype(int))
        if 0 not in eps:
            if eps not in found:
                found.add(eps)
                chambers.append(eps)
    chamber_pairs = []
    seen = set()
    for eps in chambers:
        if eps not in seen:
            chamber_pairs.append(eps)
            seen.add(eps)
            seen.add(tuple(-x for x in eps))
    return chamber_pairs, chambers

def exact_farkas(A):
    # We want y >= 0, sum(y) == 1, A.T @ y <= 0
    # Let's find one using scipy, then reconstruct exact.
    m, n = A.shape
    c = np.zeros(m)
    # A.T y <= 0 ->  y >= 0
    # sum(y) == 1
    A_eq = np.ones((1, m))
    b_eq = np.array([1.0])
    res = linprog(c, A_ub=A.T, b_ub=np.zeros(n), A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        return None
    
    # Reconstruct exact y
    # Support of y:
    y_float = res.x
    supp_y = np.where(y_float > 1e-7)[0]
    # Active constraints in A.T y <= 0
    slack = np.zeros(n) - A.T @ y_float
    supp_s = np.where(slack < 1e-7)[0] # active tight inequalities A.T y == 0
    
    # Let's set up a Sympy linear system
    # y[i] for i in supp_y
    y_vars = sympy.symbols(f'y0:{len(supp_y)}')
    eqs = []
    eqs.append(sum(y_vars) - 1)
    for j in supp_s:
        eqs.append(sum(A[i, j] * y_vars[idx] for idx, i in enumerate(supp_y)))
    
    sol = sympy.solve(eqs, y_vars)
    if not sol and len(supp_s) > 0:
        # maybe overdetermined, try solving with subset
        pass
        
    if isinstance(sol, dict) and sol:
        y_exact = [sympy.Rational(0)] * m
        for idx, i in enumerate(supp_y):
            val = sol.get(y_vars[idx], 0)
            if not isinstance(val, (int, sympy.Rational)):
                # free variable? pick 1 or something if possible.
                try:
                    val = val.subs({v: sympy.Rational(1, 10) for v in val.free_symbols})
                except:
                    pass
            y_exact[i] = val
            
        # check
        y_vec = sympy.Matrix(y_exact)
        A_sym = sympy.Matrix(A)
        ATy = A_sym.T * y_vec
        valid = True
        for v in ATy:
            if v > 0:
                valid = False
        for v in y_vec:
            if v < 0:
                valid = False
        if valid:
            return [str(v) for v in y_exact]
            
    # Fallback to float if exact fails, though we want exact
    return "Float fallback: " + str(y_float)

def main():
    U = get_U()
    classes = build_classes(U)
    chamber_pairs, chambers = build_chambers(U)
    
    ch_classes = []
    for eps in chamber_pairs:
        eps = np.array(eps)
        lst = []
        for i, j, r, cidx in classes:
            d = eps * (U @ r)
            mask = np.ones(len(U), bool)
            mask[[i,j]] = False
            if np.all(d[mask] > 1e-9) or np.all(d[mask] < -1e-9):
                lst.append(cidx)
        ch_classes.append(lst)
    
    valid_assignments = []
    for sig in itertools.product([1, -1], repeat=10):
        ok = True
        for lst in ch_classes:
            vals = [sig[cidx] for cidx in lst]
            if len(set(vals)) < 2:
                ok = False
                break
        if ok:
            valid_assignments.append(sig)
            
    results = []
    all_infeasible = True
    
    for sig in valid_assignments:
        for k in [2, 3]:
            # Construct A matrix for w > 0: sig_cidx * W_cidx > 0
            A = np.zeros((10, len(U)))
            for i, j, r, cidx in classes:
                for t in range(len(U)):
                    if t in (i, j):
                        continue
                    # |<u_t, r>| is |det(u_t, u_i, u_j)|
                    # we can use exact determinant
                    det = np.linalg.det([U[t], U[i], U[j]])
                    val = round(abs(det)) # since U is integer, det is integer
                    s_t = 1 if t < k else -1
                    A[cidx, t] = sig[cidx] * s_t * val
                    
            # Check feasibility
            # w > 0 => Aw > 0
            # max 0 s.t. -A w <= -1 (equivalent to Aw >= 1)
            res = linprog(np.zeros(len(U)), A_ub=-A, b_ub=-np.ones(10), bounds=(1, None), method="highs")
            
            if res.success:
                all_infeasible = False
                results.append({"sig": sig, "k": k, "feasible": True})
            else:
                cert = exact_farkas(A)
                results.append({"sig": sig, "k": k, "feasible": False, "farkas": cert})

    print(f"All infeasible? {all_infeasible}")
    with open("farkas_t0.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
