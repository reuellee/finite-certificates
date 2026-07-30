"""Exactify a zonoboxtope instance and certify its EXACT vertex count.

Input json: either {M, U, a, b} (segments m_i + [-u_i,u_i], coefficients
a_i, b_i >= 0) or the T-form {U, al, be, k, T} (converted via
m_0 = T/al_0, a = (2*al, be), b = (al, 2*be)).

Output cert json: rational instance + per-vertex witness directions +
per-non-vertex convex-combination certificates, such that a standalone
Fraction-only verifier can pin f0 exactly.

BUILD TOOL (floats allowed); the verifier is the exact half.
Usage: python build_cert_extremal.py in.json out_cert.json <claimed_f0>
"""
import sys, json, itertools
import numpy as np
from fractions import Fraction
from scipy.spatial import ConvexHull
from scipy.optimize import linprog


def load_instance(path):
    d = json.load(open(path))
    if "a" in d:
        M, U = np.array(d["M"]), np.array(d["U"])
        a, b = np.array(d["a"]), np.array(d["b"])
    else:
        U = np.array(d["U"]); T = np.array(d["T"])
        al, be = np.array(d["al"]), np.array(d["be"])
        M = np.zeros_like(U); M[0] = T / al[0]
        a = np.concatenate([2 * al, be]); b = np.concatenate([al, 2 * be])
    return M, U, a, b


def pts_float(M, U, a, b):
    n = len(a)
    S = np.array(list(itertools.product([-1.0, 1.0], repeat=n)))
    return np.vstack([(a[:, None] * M).sum(0) + S @ (a[:, None] * U),
                      (b[:, None] * M).sum(0) + S @ (b[:, None] * U)])


def hull_count(P):
    Q = np.unique(np.round(P, 9), axis=0)
    try:
        return len(ConvexHull(Q).vertices)
    except Exception:
        return 0


def rationalize(M, U, a, b, want):
    for den in (30, 100, 400, 2000, 20000, 10**6):
        Mr = [[Fraction(x).limit_denominator(den) for x in r] for r in M]
        Ur = [[Fraction(x).limit_denominator(den) for x in r] for r in U]
        ar = [Fraction(x).limit_denominator(den) for x in a]
        br = [Fraction(x).limit_denominator(den) for x in b]
        Pf = pts_float(np.array(Mr, float), np.array(Ur, float),
                       np.array(ar, float), np.array(br, float))
        c = hull_count(Pf)
        print(f"  den={den}: count after rounding = {c}")
        if c == want:
            return Mr, Ur, ar, br
    sys.exit("rationalization destroyed the count")


def exact_points(Mr, Ur, ar, br):
    n, d = len(Ur), len(Ur[0])
    pts = []
    for coef in (ar, br):
        cen = [sum(coef[i] * Mr[i][j] for i in range(n)) for j in range(d)]
        for s in itertools.product((-1, 1), repeat=n):
            pts.append(tuple(cen[j] + sum(s[i] * coef[i] * Ur[i][j]
                                          for i in range(n)) for j in range(d)))
    return pts


def witness(Pf, i, d):
    diffs = Pf[i] - np.delete(Pf, i, axis=0)
    c = diffs.mean(0)
    for _ in range(400000):
        m = diffs @ c
        j = int(np.argmin(m))
        if m[j] > 1e-7 * (np.linalg.norm(c) + 1e-12):
            return c / np.abs(c).max()
        c = c + diffs[j]
    return None


def exact_witness_ok(cr, pts, i, d):
    vals = [sum(cr[k] * p[k] for k in range(d)) for p in pts]
    return all(vals[j] < vals[i] for j in range(len(pts)) if j != i)


def combo_cert(Pf, verts_idx, i, pts, d):
    """p_i = convex combo of hull VERTICES: float LP -> exact solve on the
    active support -> verify."""
    Vs = [v for v in verts_idx if v != i]
    A_eq = np.vstack([Pf[Vs].T, np.ones(len(Vs))])
    b_eq = np.concatenate([Pf[i], [1.0]])
    r = linprog(c=np.zeros(len(Vs)), A_eq=A_eq, b_eq=b_eq,
                bounds=[(0, None)] * len(Vs), method="highs")
    if r.status != 0:
        return None
    lam = r.x
    sup = [Vs[t] for t in range(len(Vs)) if lam[t] > 1e-9]
    if len(sup) > d + 1:                       # trim to a Caratheodory support
        order = np.argsort(-lam)
        sup = [Vs[t] for t in order[:d + 1]]
    # exact solve on support (pad with more vertices if singular)
    from fractions import Fraction as F
    for extra in range(0, 6):
        cand = sup + [v for v in Vs if v not in sup][:extra]
        m = len(cand)
        # solve sum_l lam_l * pts[cand[l]] = pts[i], sum lam = 1 exactly
        rows = [[pts[c0][j] for c0 in cand] for j in range(d)] + [[F(1)] * m]
        rhs = list(pts[i]) + [F(1)]
        sol = exact_lsq(rows, rhs, m)
        if sol is not None and all(x >= 0 for x in sol):
            return [(cand[t], sol[t]) for t in range(m) if sol[t] > 0]
    return None


def exact_lsq(rows, rhs, m):
    """Gaussian elimination over Fractions for the (d+1) x m system; returns
    one solution or None. Free variables set to 0."""
    R = [row[:] + [rhs[t]] for t, row in enumerate(rows)]
    nr, nc = len(R), m
    piv = []
    ri = 0
    for c in range(nc):
        pr = next((r for r in range(ri, nr) if R[r][c] != 0), None)
        if pr is None:
            continue
        R[ri], R[pr] = R[pr], R[ri]
        pv = R[ri][c]
        R[ri] = [x / pv for x in R[ri]]
        for r in range(nr):
            if r != ri and R[r][c] != 0:
                f = R[r][c]
                R[r] = [x - f * y for x, y in zip(R[r], R[ri])]
        piv.append(c)
        ri += 1
        if ri == nr:
            break
    for r in range(ri, nr):
        if R[r][nc] != 0:
            return None                        # inconsistent
    sol = [Fraction(0)] * m
    for t, c in enumerate(piv):
        sol[c] = R[t][nc]
    return sol


def main():
    inp, outp, want = sys.argv[1], sys.argv[2], int(sys.argv[3])
    M, U, a, b = load_instance(inp)
    n, d = U.shape
    print(f"instance ({d},{n}), target f0 = {want}")
    Mr, Ur, ar, br = rationalize(M, U, a, b, want)
    pts = exact_points(Mr, Ur, ar, br)
    assert len(set(pts)) == len(pts) == 2 ** (n + 1), "candidates not distinct"
    Pf = np.array([[float(x) for x in p] for p in pts])
    hull = ConvexHull(np.array(Pf))
    vidx = sorted(set(int(v) for v in hull.vertices))
    print(f"float hull: {len(vidx)} vertices")
    assert len(vidx) == want, "hull count mismatch after exactification"
    wits, combos = {}, {}
    for i in range(len(pts)):
        if i in vidx:
            c = witness(Pf, i, d)
            assert c is not None, f"no witness for vertex {i}"
            ok = False
            for den in (10**4, 10**6, 10**9):
                cr = [Fraction(x).limit_denominator(den) for x in c]
                if exact_witness_ok(cr, pts, i, d):
                    ok = True; break
            assert ok, f"exact witness failed for vertex {i}"
            wits[i] = [str(x) for x in cr]
        else:
            cc = combo_cert(Pf, vidx, i, pts, d)
            assert cc is not None, f"no combo certificate for non-vertex {i}"
            combos[i] = [[j, str(l)] for j, l in cc]
    print(f"{len(wits)} witnesses, {len(combos)} combo certificates")
    json.dump(dict(d=int(d), n=int(n), f0=want,
                   M=[[str(x) for x in r] for r in Mr],
                   U=[[str(x) for x in r] for r in Ur],
                   a=[str(x) for x in ar], b=[str(x) for x in br],
                   witnesses={str(k): v for k, v in wits.items()},
                   combos={str(k): v for k, v in combos.items()}),
              open(outp, "w"))
    print("wrote", outp)


if __name__ == "__main__":
    main()
