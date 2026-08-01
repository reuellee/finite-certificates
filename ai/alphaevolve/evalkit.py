"""Deterministic sandboxed evaluation of an evolved search program.

Contract with the evolved program (file `main.py`):

    search(d, n, rng, nverts, budget) -> (M, U, a, b)

* `nverts(M, U, a, b)` returns the float vertex count of that instance and
  costs one unit of budget; it raises `BudgetExhausted` past `budget` calls.
* The harness records the best instance seen across EVERY `nverts` call, so a
  program that crashes, loops, or returns junk still scores whatever it found.
* `rng` is a seeded numpy Generator.  Fixed seeds + a fixed CALL budget (never
  a wall-clock budget) make the score a deterministic function of the program:
  the same program always gets the same score, so a monotonic hill-climber
  cannot be fooled by a lucky machine-load draw.

Metrics submitted to AlphaEvolve (both maximised):
  vertices  -- best exact-checked-if-record vertex count found (integer)
  robustness-- mean count over 8 tiny perturbations of the best instance.
               Near-continuous, so the 58 / 84 plateau has a gradient, and a
               count that exists only as a float-hull artefact scores worse.
"""
import json
import os
import sys
import traceback

import numpy as np
import zbx


class BudgetExhausted(Exception):
    pass


class Harness:
    def __init__(self, d, n, budget):
        self.d, self.n, self.budget = d, n, budget
        self.calls = 0
        self.best = -1
        self.best_inst = None

    def nverts(self, M, U, a, b):
        if self.calls >= self.budget:
            raise BudgetExhausted(f"budget {self.budget} exhausted")
        self.calls += 1
        M = np.asarray(M, float).reshape(self.n, self.d)
        U = np.asarray(U, float).reshape(self.n, self.d)
        a = np.asarray(a, float).reshape(self.n)
        b = np.asarray(b, float).reshape(self.n)
        if not (np.all(np.isfinite(M)) and np.all(np.isfinite(U))
                and np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
            return 0
        if np.any(a < 0) or np.any(b < 0):        # model requires a, b >= 0
            return 0
        v = zbx.nverts_float(M, U, a, b)
        if v > zbx.cap(self.d, self.n):           # impossible: evaluator bug
            raise RuntimeError(f"count {v} exceeds cap {zbx.cap(self.d, self.n)}")
        if v > self.best:
            self.best = v
            self.best_inst = (M.copy(), U.copy(), a.copy(), b.copy())
        return v


def robustness(M, U, a, b, k=8, scale=1e-4, seed=7):
    """Mean vertex count over k tiny relative perturbations of the instance.

    A second, near-continuous Pareto axis.  It rewards counts that survive
    perturbation and punishes counts that only exist because several candidate
    points happen to coincide or a facet happens to be flat -- i.e. exactly the
    float-hull artefacts that must never be allowed to look like progress.  A
    genuinely extremal instance keeps its count (strict witnesses persist under
    small perturbations), so this cannot penalise a real record.
    """
    rng = np.random.default_rng(seed)
    M, U = np.asarray(M, float), np.asarray(U, float)
    a, b = np.asarray(a, float), np.asarray(b, float)
    sM = scale * (np.abs(M).mean() + 1e-9)
    sU = scale * (np.abs(U).mean() + 1e-9)
    sa = scale * (np.abs(a).mean() + 1e-9)
    tot = 0.0
    for _ in range(k):
        tot += zbx.nverts_float(M + rng.normal(scale=sM, size=M.shape),
                                U + rng.normal(scale=sU, size=U.shape),
                                np.maximum(a + rng.normal(scale=sa, size=a.shape), 0),
                                np.maximum(b + rng.normal(scale=sa, size=b.shape), 0))
    return tot / k


def run(program_path, d, n, budget, seeds):
    """Import the program, run `search` once per seed, return the harness best."""
    src = open(program_path, encoding="utf-8").read()
    g = {"__name__": "evolved", "np": np}
    err = None
    best, best_inst, per_seed = -1, None, []
    try:
        exec(compile(src, "main.py", "exec"), g)
        fn = g.get("search")
        if fn is None:
            raise RuntimeError("program defines no search(d, n, rng, nverts, budget)")
    except Exception:                                            # noqa: BLE001
        return {"vertices": 0, "robustness": 0.0, "per_seed": [],
                "error": traceback.format_exc(limit=4)[-1500:], "calls": 0}

    calls = 0
    for s in seeds:
        h = Harness(d, n, budget // len(seeds))
        try:
            fn(d, n, np.random.default_rng(s), h.nverts, h.budget)
        except BudgetExhausted:
            pass
        except Exception:                                        # noqa: BLE001
            err = traceback.format_exc(limit=4)[-1500:]
        calls += h.calls
        per_seed.append(h.best)
        if h.best > best:
            best, best_inst = h.best, h.best_inst

    rob = 0.0
    if best_inst is not None:
        try:
            rob = robustness(*best_inst)
        except Exception:                                        # noqa: BLE001
            pass
    out = {"vertices": int(max(best, 0)), "robustness": float(rob),
           "per_seed": per_seed, "calls": calls}
    if err:
        out["error"] = err
    if best_inst is not None:
        M, U, a, b = best_inst
        out["instance"] = {"M": M.tolist(), "U": U.tolist(),
                           "a": a.tolist(), "b": b.tolist()}
    return out


if __name__ == "__main__":
    # argv: program_path d n budget seed[,seed...]
    p, d, n, budget, seeds = sys.argv[1:6]
    r = run(p, int(d), int(n), int(budget), [int(x) for x in seeds.split(",")])
    sys.stdout.write("<<<RESULT>>>" + json.dumps(r))
