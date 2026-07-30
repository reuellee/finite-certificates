import sys
import numpy as np
from sympy import symbols, simplify

def generate_valid_U(rng, target_sgns):
    while True:
        U = rng.integers(-20, 20, size=(5, 3))
        if np.linalg.matrix_rank(U) < 3:
            continue
        try:
            sgns = [
                np.sign(np.linalg.det(U[[0,1,2]])),
                np.sign(np.linalg.det(U[[0,1,3]])),
                np.sign(np.linalg.det(U[[0,1,4]])),
                np.sign(np.linalg.det(U[[0,2,3]])),
                np.sign(np.linalg.det(U[[0,2,4]])),
                np.sign(np.linalg.det(U[[0,3,4]])),
                np.sign(np.linalg.det(U[[1,2,3]])),
                np.sign(np.linalg.det(U[[1,2,4]])),
                np.sign(np.linalg.det(U[[1,3,4]])),
                np.sign(np.linalg.det(U[[2,3,4]]))
            ]
        except:
            continue
        if 0 in sgns:
            continue
        if sgns == target_sgns or sgns == [-x for x in target_sgns]:
            return U

def main():
    rng = np.random.default_rng(2026)
    target = [1, 1, -1, -1, -1, -1, -1, 1, -1, -1]
    
    print("Sub-problem: Determinant Identities Verification")
    print("Generating 20 exact rational configurations...")
    
    success_count = 0
    num_trials = 20
    
    for trial in range(num_trials):
        U = generate_valid_U(rng, target)
        
        # Calculate exact integer absolute determinants
        D = {}
        for i in range(5):
            for j in range(i+1, 5):
                for k in range(j+1, 5):
                    # determinant is exact integer
                    val = int(round(np.linalg.det(U[[i,j,k]])))
                    D[f"{i}{j}{k}"] = abs(val)
                    
        # Define symbolic positive weights
        v = symbols('v0 v1 v2 v3 v4', positive=True)
        
        # Evaluate E expressions based on normalized formulation
        # E_ij = sum_{t} s_t v_t D_tij
        # Split k=3 means s0=1, s1=1, s2=1, s3=-1, s4=-1
        E_02 = v[1] * D["012"] - v[3] * D["023"] - v[4] * D["024"]
        E_24 = v[0] * D["024"] + v[1] * D["124"] - v[3] * D["234"]
        E_13 = v[0] * D["013"] + v[2] * D["123"] - v[4] * D["134"]
        E_03 = v[1] * D["013"] + v[2] * D["023"] - v[4] * D["034"]
        
        # Evaluate coefficients based on GP relations
        c1 = D["013"] * D["234"]
        c2 = D["013"] * D["023"]
        c3 = D["024"] * D["023"]
        c4 = D["024"] * D["123"]
        
        # Verify Identity: c2*E_24 + c4*E_03 - c1*E_02 - c3*E_13 == 0
        lhs = c2 * E_24 + c4 * E_03
        rhs = c1 * E_02 + c3 * E_13
        diff = simplify(lhs - rhs)
        
        assert diff == 0, f"Identity failed on trial {trial}"
        assert c1 > 0 and c2 > 0 and c3 > 0 and c4 > 0, "Coefficients not strictly positive"
        success_count += 1
        
    print(f"Verified identity exactly across {success_count}/{num_trials} configurations.")
    
if __name__ == "__main__":
    main()
