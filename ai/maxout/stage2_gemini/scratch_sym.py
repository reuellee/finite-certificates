import sys
from sympy import symbols, Matrix, simplify, factor

def get_symbolic_nullspace():
    # Variables for the absolute determinants we need
    # The matrix M has entries: D024, D014, D013, D012, D124, D123, D023, D234, D134, D034
    vars_str = "D024 D014 D013 D012 D124 D123 D023 D234 D134 D034"
    D = {v: symbols(v, positive=True) for v in vars_str.split()}
    
    # M: columns E02, E24, E13, E03
    M = Matrix([
        [0, D["D024"], D["D013"], 0],
        [D["D012"], D["D124"], 0, D["D013"]],
        [0, 0, D["D123"], D["D023"]],
        [-D["D023"], -D["D234"], 0, 0],
        [-D["D024"], 0, -D["D134"], -D["D034"]]
    ])
    
    # We want to find a vector c = [c02, c24, c13, c03]^T such that M*c = 0.
    # We can just take any 4 rows of M and compute the null vector (e.g. by cross product / cofactors)
    # Let's take rows 0, 2, 3, 4
    M_sub = M[[0, 2, 3, 4], :]
    
    # The null vector components are the cofactors of a row if we imagine appending it to a 4x4 matrix.
    # So we can just take the adjoint, or just ask sympy.
    print("Computing symbolic nullspace...")
    ns = M_sub.nullspace()
    print("Nullspace dimension:", len(ns))
    
    if len(ns) > 0:
        c = ns[0]
        # To clear denominators, we can multiply by the LCM of denominators.
        c = c * c[-1].as_numer_denom()[1]  # roughly clear denom
        c = simplify(c)
        for i, val in enumerate(c):
            print(f"c[{i}] =", factor(val))
            
get_symbolic_nullspace()
