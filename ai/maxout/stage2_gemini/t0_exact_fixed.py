"""Self-consistent T0 certificate chain (review repair of t0_exact.py).

Fixes the labeling gap: the valid class assignments are enumerated from the
chamber incidence of U_ints ITSELF (facet_lp.build), then every
(assignment, split) system is proven infeasible with exact rational Farkas
multipliers (primal-margin LP duals, exact-repaired on the active support,
verified in pure Fraction arithmetic). Writes farkas_t0_exact.json.

Run from ai/maxout/:  python stage2_gemini/t0_exact_fixed.py
Requires numpy + scipy for the float LP hints; every certificate is
verified exactly before serialization.
"""
import json, os, sys
import numpy as np
from fractions import Fraction
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import facet_lp

U_INTS = [[-6, -13, 18], [-9, -12, 8], [-13, -4, 16], [4, -19, -8], [16, 15, -12]]
PAIRS = [(i, j) for i in range(5) for j in range(i + 1, 5)]


def det3(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


DMAP = {(t, i, j): abs(det3(U_INTS[t], U_INTS[i], U_INTS[j]))
        for t in range(5) for (i, j) in PAIRS if t not in (i, j)}


def build_A(S, k):
    s = [1] * k + [-1] * (5 - k)
    return [[Fraction(S[ci]) * s[t] * DMAP[(t, i, j)] if t not in (i, j)
             else Fraction(0) for t in range(5)]
            for ci, (i, j) in enumerate(PAIRS)]


def exact_cert(S, k):
    A = build_A(list(S), k)
    Af = np.array([[float(x) for x in r] for r in A])
    A_ub = np.hstack([-Af, np.ones((10, 1))])
    r = linprog(c=[0] * 5 + [-1.0], A_ub=A_ub, b_ub=np.zeros(10),
                A_eq=[[1] * 5 + [0]], b_eq=[1.0],
                bounds=[(0, None)] * 5 + [(None, None)], method="highs")
    if r.status != 0:
        return "LPFAIL", None
    if r.x[5] > 1e-9:
        return "FEASIBLE", float(r.x[5])
    y_f = -np.array(r.ineqlin.marginals)

    def check(y):
        return (all(v >= 0 for v in y) and any(v > 0 for v in y)
                and all(sum(y[c] * A[c][t] for c in range(10)) <= 0
                        for t in range(5)))

    y = [Fraction(v).limit_denominator(10 ** 7) for v in y_f]
    if check(y):
        return "CERT", y
    sup = [c for c in range(10) if y_f[c] > 1e-9]
    tight = [t for t in range(5)
             if abs(sum(float(A[c][t]) * y_f[c] for c in range(10))) < 1e-5]
    rows = [[A[c][t] for c in sup] for t in tight] + [[Fraction(1)] * len(sup)]
    rhs = [Fraction(0)] * len(tight) + [Fraction(1)]
    M = [row[:] + [rhs[i]] for i, row in enumerate(rows)]
    nr, nc = len(M), len(sup)
    ri, piv = 0, []
    for cc in range(nc):
        pr = next((rr for rr in range(ri, nr) if M[rr][cc] != 0), None)
        if pr is None:
            continue
        M[ri], M[pr] = M[pr], M[ri]
        pv = M[ri][cc]
        M[ri] = [x / pv for x in M[ri]]
        for rr in range(nr):
            if rr != ri and M[rr][cc] != 0:
                f = M[rr][cc]
                M[rr] = [a - f * b for a, b in zip(M[rr], M[ri])]
        piv.append(cc)
        ri += 1
    if any(M[rr][nc] != 0 for rr in range(ri, nr)):
        return "REPAIRFAIL", None
    y2 = [Fraction(0)] * 10
    for t2, cc in enumerate(piv):
        y2[sup[cc]] = M[t2][nc]
    return ("CERT", y2) if check(y2) else ("REPAIRFAIL", None)


def main():
    Un = np.array(U_INTS, float)
    Un /= np.linalg.norm(Un, axis=1, keepdims=True)
    built = None
    for _ in range(20):                      # build() samples chambers randomly
        cand = facet_lp.build(Un, 2)
        if cand and len(cand[1]) == 22:
            built = cand
            break
    assert built, "U_ints must be generic with 22 chambers"
    _, _, ch_rays = built
    valid = []
    for bits in range(1024):
        S = [1 if bits >> c & 1 else -1 for c in range(10)]
        if all(len({S[sd // 2] for sd in lst}) > 1 for lst in ch_rays):
            valid.append(tuple(S))
    assert len(valid) == 200, f"expected 200 valid assignments, got {len(valid)}"
    certs, bad = [], []
    for S in valid:
        for k in (2, 3):
            st, val = exact_cert(S, k)
            if st == "CERT":
                certs.append(dict(sig=list(S), k=k, feasible=False,
                                  farkas=[str(v) for v in val]))
            else:
                bad.append((S, k, st))
    if bad:
        print("FAILURES:", bad)
        sys.exit(1)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "farkas_t0_exact.json")
    json.dump(dict(U_ints=U_INTS,
                   labeling="incidence derived from U_ints itself",
                   n_valid=len(valid),
                   note="exact rational Farkas certs; y>=0, y!=0, A^T y<=0 in "
                        "Fractions; A[c][t]=S_c*s_t*|det(U_t,U_i,U_j)|, "
                        "s=(+1^k,-1^(5-k)). Proves: NO valid class assignment "
                        "of U_ints' own chamber structure is realizable at T=0 "
                        "with positive weights.",
                   certificates=certs), open(out, "w"))
    print(f"wrote {len(certs)} exact certificates to {out}")


if __name__ == "__main__":
    main()
