import sys
sys.path.append('.')
import numpy as np
from sympy import Matrix, symbols, simplify

def test():
    rng = np.random.default_rng(123)
    
    # We want 20 exact configurations to test an algebraic identity.
    # First, let's find the identity algebraically or with one exact config.
    while True:
        U = rng.integers(-10, 10, size=(5, 3))
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
        target = [1, 1, -1, -1, -1, -1, -1, 1, -1, -1]
        if sgns == target or sgns == [-x for x in target]:
            break
            
    print("Found exact U!")
    D = {}
    for i in range(5):
        for j in range(i+1, 5):
            for k in range(j+1, 5):
                det_val = int(round(np.linalg.det(U[[i,j,k]])))
                D[f"{i}{j}{k}"] = abs(det_val)
                
    # matrix for 4 classes: (0,2), (2,4), (1,3), (0,3)
    # The columns are E_02, E_24, E_13, E_03
    M = Matrix([
        [0, D["024"], D["013"], 0],
        [D["012"], D["124"], 0, D["013"]],
        [0, 0, D["123"], D["023"]],
        [-D["023"], -D["234"], 0, 0],
        [-D["024"], 0, -D["134"], -D["034"]]
    ])
    
    print("Rank of M:", M.rank())
    ns = M.nullspace()
    print("Nullspace:")
    for n in ns:
        print(n)

test()
