import numpy as np
from scipy.optimize import linprog
import sympy as sp
import itertools
import json
import sys

def main():
    print("Starting exact T0 problem solver...")

    # 1. Exact generic U vectors
    U_ints = [
        [-6, -13, 18],
        [-9, -12, 8],
        [-13, -4, 16],
        [4, -19, -8],
        [16, 15, -12]
    ]
    norms = [23, 17, 21, 21, 25]

    U_rational = [[f"{u}/{n}" for u in u_vec] for u_vec, n in zip(U_ints, norms)]

    # 2. Extract classes and M_base
    classes = []
    M_base = np.zeros((10, 5), dtype=object)
    idx = 0
    for i in range(5):
        for j in range(i+1, 5):
            r = np.cross(U_ints[i], U_ints[j])
            classes.append((i, j, r))
            for t in range(5):
                if t != i and t != j:
                    s_t = 1 if t < 3 else -1
                    # Exact integer absolute determinant
                    M_base[idx, t] = s_t * abs(np.dot(U_ints[t], r))
            idx += 1

    # 3. Exactly enumerate the 22 chambers
    chambers = []
    for eps in itertools.product([-1, 1], repeat=5):
        A = []
        for t in range(5):
            A.append( -eps[t] * np.array(U_ints[t]) )
        res = linprog(c=[0,0,0], A_ub=A, b_ub=[-1]*5, bounds=(None, None))
        if res.success: chambers.append(eps)
    
    print(f"Found {len(chambers)} chambers")

    pairs = []
    seen = set()
    for eps in chambers:
        if eps not in seen:
            pairs.append(eps)
            seen.add(eps)
            seen.add(tuple(-x for x in eps))
    
    print(f"Grouped into {len(pairs)} antipodal pairs")

    # 4. Find valid assignments (NAE on chamber incident sides)
    pair_incidences = []
    for p in pairs:
        inc = []
        for c_idx, (i, j, dets) in enumerate(classes):
            signs = []
            for t in range(5):
                if t != i and t != j:
                    signs.append( np.sign(p[t] * np.dot(U_ints[t], classes[c_idx][2])) )
            if len(set(signs)) == 1 and 0 not in signs:
                inc.append(c_idx)
        pair_incidences.append(inc)

    valid_assignments = []
    for S in itertools.product([-1, 1], repeat=10):
        valid = True
        for inc in pair_incidences:
            vals = set([S[c] for c in inc])
            if len(vals) < 2:
                valid = False
                break
        if valid: valid_assignments.append(S)

    print(f"Found {len(valid_assignments)} valid assignments")

    output_data = {
        "U_rational": U_rational,
        "results": []
    }

    # 5. Solve Exact Farkas
    feasible_found = False
    for s_idx, S in enumerate(valid_assignments):
        A = np.zeros((10, 5), dtype=int)
        for c in range(10):
            for t in range(5):
                A[c, t] = S[c] * M_base[c, t]
        
        # We check feasibility of A w > 0, w > 0
        # Farkas alternative: y >= 0, sum y = 1, A^T y <= 0
        res = linprog(c=[0]*10, A_ub=A.T, b_ub=[0]*5, A_eq=[[1]*10], b_eq=[1], bounds=[(0, None)]*10, method='highs')
        
        if not res.success:
            print(f"Assignment {s_idx} is FEASIBLE!")
            # Find feasible w
            res_w = linprog(c=[0]*5, A_ub=-A, b_ub=[-1]*5, bounds=[(1, None)]*5, method='highs')
            if res_w.success:
                w_float = res_w.x
                output_data["results"].append({
                    "assignment": S,
                    "feasible": True,
                    "witness_float": w_float.tolist()
                })
                feasible_found = True
            continue
        
        y_float = res.x
        # Robust extraction
        # Try to find exactly one ray
        y_exact = None
        
        # Sort indices by proximity to zero to find the most active constraints
        # Try different thresholds if first fails
        for thresh in [1e-6, 1e-5, 1e-7]:
            J = [c for c in range(10) if y_float[c] > thresh]
            K = [t for t in range(5) if np.dot(A.T[t], y_float) > -thresh]
            
            if not J: continue
            
            M_eq = sp.Matrix([[A[c, t] for c in J] for t in K])
            ns = M_eq.nullspace()
            
            if len(ns) == 1:
                v = ns[0]
                lcm = sp.lcm([sp.Rational(val).q for val in v])
                v = v * lcm
                if v[0] < 0: v = -v
                
                cand_y = [0]*10
                for idx_j, c in enumerate(J):
                    cand_y[c] = int(v[idx_j])
                
                cand_y = np.array(cand_y, dtype=object)
                AT_y = cand_y @ A
                if np.all(cand_y >= 0) and np.all(AT_y <= 0) and np.any(cand_y > 0):
                    y_exact = cand_y.tolist()
                    break

        if y_exact is None:
            # Fallback to limit_denominator
            from fractions import Fraction
            cand_y = [Fraction(val).limit_denominator(1000000) for val in y_float]
            lcm = np.lcm.reduce([val.denominator for val in cand_y])
            cand_y = [int(val * lcm) for val in cand_y]
            cand_y = np.array(cand_y, dtype=object)
            AT_y = cand_y @ A
            if np.all(cand_y >= 0) and np.all(AT_y <= 0) and np.any(cand_y > 0):
                y_exact = cand_y.tolist()
        
        if y_exact is None:
            print(f"FAILED to exactify assignment {s_idx}")
            sys.exit(1)
            
        output_data["results"].append({
            "assignment": S,
            "farkas_multipliers": [str(val) for val in y_exact],
            "verified": True
        })
        
        if s_idx % 10 == 0:
            print(f"Processed {s_idx}/200...")

    with open("farkas_t0.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    if not feasible_found:
        print("All assignments are INFEASIBLE. Certificates written.")
    else:
        print("Some assignments were FEASIBLE.")

if __name__ == "__main__":
    main()
