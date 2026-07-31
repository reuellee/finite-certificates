import json
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction
import sympy as sp

# 1. Generate generic U and rationalize
rng = np.random.default_rng(42)
U_float = rng.normal(size=(5, 3))
U_float /= np.linalg.norm(U_float, axis=1, keepdims=True)

# Rationalize U: we can just take U_float and round to small fractions, e.g., denominator 100
U_frac = []
for i in range(5):
    row = []
    for j in range(3):
        f = Fraction(U_float[i, j]).limit_denominator(100)
        row.append(f)
    U_frac.append(row)

# Re-check genericity (all 3x3 determinants non-zero)
for i in range(5):
    for j in range(i+1, 5):
        for k in range(j+1, 5):
            det = U_frac[i][0]*(U_frac[j][1]*U_frac[k][2] - U_frac[j][2]*U_frac[k][1]) - \
                  U_frac[i][1]*(U_frac[j][0]*U_frac[k][2] - U_frac[j][2]*U_frac[k][0]) + \
                  U_frac[i][2]*(U_frac[j][0]*U_frac[k][1] - U_frac[j][1]*U_frac[k][0])
            if det == 0:
                print("Not generic!")
                exit(1)

U = np.array([[float(x) for x in row] for row in U_frac])

# Compute classes and chambers using facet_lp logic
n = 5
classes = []
for i in range(n):
    for j in range(i + 1, n):
        r = np.cross(U[i], U[j])
        r = r / np.linalg.norm(r)
        classes.append((i, j, r))

# Get chambers
dirs = [c[2] + rng.normal(scale=1e-4, size=3) for c in classes for _ in range(8)]
dirs += [-d for d in dirs] + list(rng.normal(size=(6 * n * n, 3)))
cham = {}
for c in dirs:
    d = U @ c
    if np.all(np.abs(d) > 1e-9):
        cham[tuple(np.sign(d).astype(int))] = True
chambers = [np.array(e) for e in cham]

print(f"Number of chambers: {len(chambers)}")

# For each chamber, which classes is it incident to?
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

# Find valid assignments for T=0
valid_assignments = []
for bits in range(1024):
    sig = [(1 if (bits & (1 << ci)) else -1) for ci in range(10)]
    ok = True
    for lst in ch_classes:
        vals = [sig[ci] for ci in lst]
        if len(set(vals)) < 2:
            ok = False
            break
    if ok:
        valid_assignments.append(sig)

print(f"Valid class assignments at T=0: {len(valid_assignments)}")

# Dump to check
with open("stage2_gemini/sub1_info.json", "w") as f:
    json.dump({"num_chambers": len(chambers), "valid_assignments": len(valid_assignments), "U_frac": [[str(x) for x in row] for row in U_frac]}, f)
