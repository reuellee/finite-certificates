import numpy as np
from fractions import Fraction
import itertools

def get_U():
    # Use a simple integer matrix for generic U
    U_int = np.array([
        [ 1,  2,  3],
        [-1,  1,  4],
        [ 2, -3,  1],
        [-3, -1,  2],
        [ 1,  4, -1]
    ])
    return U_int

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
    # Enumerate all 2^5 = 32 sign vectors, keep realizable ones
    # A sign vector is realizable if there exists c in R^3 s.t. sign(U @ c) == eps
    # In 3D, for 5 generic planes, there are 2 * (1 + 4 + 6) = 22 chambers.
    chambers = []
    # Test a bunch of random points to find all 22 chambers
    np.random.seed(42)
    found = set()
    for _ in range(100000):
        c = np.random.randn(3)
        eps = tuple(np.sign(U @ c).astype(int))
        if 0 not in eps:
            if eps not in found:
                found.add(eps)
                chambers.append(eps)
    # Filter to antipodal pairs (just take eps with eps[0] == 1)
    # Wait, eps[0] might not split them evenly. Just pick one from each pair.
    chamber_pairs = []
    seen = set()
    for eps in chambers:
        if eps not in seen:
            chamber_pairs.append(eps)
            seen.add(eps)
            seen.add(tuple(-x for x in eps))
    return chamber_pairs, chambers

def main():
    U = get_U()
    classes = build_classes(U)
    chamber_pairs, chambers = build_chambers(U)
    print(f"Found {len(chamber_pairs)} chamber pairs (total {len(chambers)} chambers)")
    
    # For each chamber, which classes does it touch?
    # eps is the sign of U @ c.
    # The normal r_ij = U_i x U_j. The side eps sees is sign(eps * (U @ r_ij)) ?
    # No. In facet_lp.py:
    # d = eps * (U @ r)
    # mask = ones; mask[[i,j]] = False
    # if all(d[mask] > 0) -> sees +r
    # if all(d[mask] < 0) -> sees -r
    # But for T=0, both +r and -r have the SAME class sign! So we just care WHICH classes it touches.
    
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
    
    print("Classes per chamber pair:", [len(c) for c in ch_classes])
    
    # Enumerate 2^10 class assignments
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
    print(f"Valid class assignments: {len(valid_assignments)}")

if __name__ == '__main__':
    main()
