"""Ray-sign LP polish: push a near-extremal config to the cap.

For chamber eps with extreme rays R(eps), bicoloredness of s_eps = T + w_eps
is equivalent (generically) to: exists rays r-, r+ with <s,r-> < 0 < <s,r+>.
Fixing a ray-pair assignment for every chamber makes ALL conditions linear in
the parameters x = (T, al, be), since w_eps = sum_A al_i eps_i u_i -
sum_B be_j eps_j u_j.  Passing chambers keep their currently witnessed pair;
failing chambers enumerate pairs; each assignment is one LP feasibility.

SEARCH TOOL ONLY (floats).  Usage: python ray_polish.py best_n5.json out.json
"""
import sys, json, itertools
import numpy as np
from scipy.optimize import linprog

import tsearch


def chamber_rays(U, eps, tol=1e-9):
    n = len(U)
    rays = []
    for i in range(n):
        for j in range(i + 1, n):
            r = np.cross(U[i], U[j])
            nr = np.linalg.norm(r)
            if nr < 1e-12:
                continue
            r = r / nr
            for sgn in (1.0, -1.0):
                c = sgn * r
                d = eps * (U @ c)
                if np.all(d > -tol):
                    rays.append(c)
    # dedupe
    out = []
    for r in rays:
        if not any(np.linalg.norm(r - o) < 1e-7 for o in out):
            out.append(r)
    return out


def w_coeffs(eps, U, k, n):
    """w_eps as a linear map of (al, be): returns C (3 x (n)) with
    w = C_A @ al + C_B @ be columns signed."""
    CA = (eps[:k, None] * U[:k]).T          # 3 x k, times al
    CB = -(eps[k:, None] * U[k:]).T         # 3 x (n-k), times be
    return CA, CB


def solve_assignment(ch, U, k, assign, wb=(0.1, 3.0), delta=1e-3):
    """LP over x = (T(3), al(k), be(n-k)) with per-chamber ray-pair signs."""
    n = len(U)
    nv = 3 + n
    A_ub, b_ub = [], []
    for eps, (rn, rp) in zip(ch, assign):
        CA, CB = w_coeffs(eps, U, k, n)
        # <T,r> + r@CA@al + r@CB@be  <= -delta   for r = rn
        row = np.concatenate([rn, rn @ CA, rn @ CB])
        A_ub.append(row); b_ub.append(-delta)
        row = np.concatenate([rp, rp @ CA, rp @ CB])
        A_ub.append(-row); b_ub.append(-delta)
    bounds = [(None, None)] * 3 + [wb] * n
    r = linprog(c=np.zeros(nv), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                bounds=bounds, method="highs")
    if r.status != 0:
        return None
    x = r.x
    return x[:3], x[3:3 + k], x[3 + k:]


def main(inp, outp):
    d = json.load(open(inp))
    U = np.array(d["U"]); al = np.array(d["al"]); be = np.array(d["be"])
    k = d["k"]; T = np.array(d["T"]); n = len(U)
    ch, ws, Gs = tsearch.prep(U, al, be, k)
    rays = [chamber_rays(U, eps) for eps in ch]
    passing, failing = [], []
    assign = []
    for idx, (eps, w, G, R) in enumerate(zip(ch, ws, Gs, rays)):
        s = T + w
        neg = [r for r in R if s @ r < -1e-9]
        pos = [r for r in R if s @ r > 1e-9]
        if neg and pos:
            passing.append(idx); assign.append((neg[0], pos[0]))
        else:
            failing.append(idx); assign.append(None)
        if not R:
            print(f"chamber {idx}: NO RAYS (degenerate)"); return
    print(f"{len(passing)} passing, {len(failing)} failing "
          f"(chambers {len(ch)}); ray counts of failing: "
          f"{[len(rays[i]) for i in failing]}")
    # enumerate ray pairs for the failing chambers
    choices = []
    for i in failing:
        R = rays[i]
        choices.append([(a, b) for a, b in itertools.permutations(R, 2)])
    tried = 0
    for combo in itertools.product(*choices):
        tried += 1
        for i, pair in zip(failing, combo):
            assign[i] = pair
        sol = solve_assignment(ch, U, k, assign)
        if sol is not None:
            T2, al2, be2 = sol
            _, ws2, Gs2 = tsearch.prep(U, al2, be2, k)
            nb = tsearch.count_T(T2, ws2, Gs2)
            print(f"LP FEASIBLE after {tried} assignments -> recount: "
                  f"{len(ch)}+{nb} = {len(ch) + nb}")
            if nb == len(ch):
                json.dump(dict(U=U.tolist(), al=al2.tolist(), be=be2.tolist(),
                               k=int(k), T=T2.tolist(), chambers=len(ch),
                               bicolored=int(nb)), open(outp, "w"), indent=1)
                print("saved", outp)
                return
    print(f"no feasible assignment ({tried} tried)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
