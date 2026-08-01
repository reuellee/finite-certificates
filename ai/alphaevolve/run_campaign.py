"""The (4,5) / (3,7) campaign.  Ready to run; blocked 2026-08-01 on the service
actually generating candidates (see the closing section of API_NOTES.md).

    python run_campaign.py 4 5 [maxPrograms] [concurrency]

Loop: acquire -> run the evolved program in a SUBPROCESS with a hard timeout ->
score -> submit.  Every candidate at or above the incumbent (58 at (4,5), 84 at
(3,7)) is re-counted EXACTLY with `zbx.nverts_exact` before it is believed, and
anything that beats the incumbent is dumped to `record_<d><n>_<f0>.json` for the
repo's own certificate builder + verifiers.

Cost control, in order:
  * `stats.inputTokenCount` / `outputTokenCount` are read after every submit and
    printed;  --max-usd aborts and DELETES the experiment when the running
    estimate crosses the ceiling.
  * maxPrograms is a hard server-side cap.
  * cleanup.py deletes the experiment on any exit path.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

import ae_api as A
import zbx

HERE = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(HERE, "_session.txt")
INCUMBENT = {(4, 5): 58, (3, 7): 84}
BUDGET = 6000                    # nverts calls per program, split over SEEDS
SEEDS = "11,22,33"
TIMEOUT_S = 180                  # wall-clock safety net only; scoring is by calls
USD_IN, USD_OUT = 4.0e-6, 24.0e-6      # per token, gemini-3.1-pro-preview


def context_text(d, n):
    return (
        f"Target: (d,n) = ({d},{n}). Best instance known to this project has "
        f"{INCUMBENT[(d, n)]} vertices; the conjectured maximum is "
        f"{INCUMBENT[(d, n)] + (2 if (d, n) == (4, 5) else 4)} and the absolute "
        f"cap is {zbx.cap(d, n)}. Beating {INCUMBENT[(d, n)]} by even one vertex "
        "is a new mathematical result. Generic random sampling and hill-climbing "
        "have already been run far past the point of diminishing returns and "
        "always stop exactly at the incumbent, so incremental improvements to "
        "the stochastic search will not work: propose structured, algebraic or "
        "symmetric constructions instead. Read the module docstring of the "
        "program for the full record of what has already been tried and failed.")


def evaluate(src, d, n):
    """Run the evolved program in a subprocess.  Never trust it in-process."""
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "main.py")
        open(p, "w", encoding="utf-8").write(src)
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "evalkit.py"), p,
                 str(d), str(n), str(BUDGET), SEEDS],
                capture_output=True, text=True, timeout=TIMEOUT_S, cwd=HERE)
        except subprocess.TimeoutExpired:
            return {"vertices": 0, "robustness": 0.0,
                    "error": f"timeout after {TIMEOUT_S}s"}
        out = r.stdout.split("<<<RESULT>>>")
        if len(out) < 2:
            return {"vertices": 0, "robustness": 0.0,
                    "error": (r.stderr or r.stdout)[-1200:] or "no result"}
        return json.loads(out[1])


def exact_gate(inst, d, n, incumbent):
    """Re-count EXACTLY.  Rationalise with escalating denominators, as
    `../maxout/build_cert_extremal.py` does -- a float count can be destroyed by
    rounding, so a single denominator is not enough."""
    for den in (30, 100, 400, 2000, 20000, 10 ** 6, 10 ** 9):
        M = [[Fraction(x).limit_denominator(den) for x in r] for r in inst["M"]]
        U = [[Fraction(x).limit_denominator(den) for x in r] for r in inst["U"]]
        a = [Fraction(x).limit_denominator(den) for x in inst["a"]]
        b = [Fraction(x).limit_denominator(den) for x in inst["b"]]
        f0 = zbx.nverts_exact(M, U, a, b)
        if f0 > incumbent:
            return f0, {"d": d, "n": n, "f0": f0, "den": den,
                        "M": [[str(x) for x in r] for r in M],
                        "U": [[str(x) for x in r] for r in U],
                        "a": [str(x) for x in a], "b": [str(x) for x in b]}
    return f0, None


def main():
    d, n = int(sys.argv[1]), int(sys.argv[2])
    max_programs = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    concurrency = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    max_usd = float(os.environ.get("AE_MAX_USD", "20"))
    incumbent = INCUMBENT[(d, n)]

    session = open(SESSION_FILE).read().strip()
    seed_src = open(os.path.join(HERE, "seed_program.py"), encoding="utf-8").read()
    seed_res = evaluate(seed_src, d, n)
    print("seed scores:", json.dumps({k: v for k, v in seed_res.items()
                                      if k != "instance"}))

    cfg = {
        "title": f"maxout-c66-d{d}n{n}",
        "problemDescription": (
            f"Maximise the number of vertices f0 of a (d,n)=({d},{n}) "
            "zonoboxtope Q = conv(Z^a u Z^b), Z^a = sum_i a_i (m_i + [-u_i,u_i]),"
            " Z^b likewise, over midpoints m_i, half-lengths u_i in R^d and "
            "nonnegative weights a, b in R^n. Write search(d, n, rng, nverts, "
            "budget) returning (M, U, a, b); nverts counts vertices and costs one"
            " unit of budget. Score = the best count found. Incumbent "
            f"{incumbent}; conjectured maximum "
            f"{incumbent + (2 if (d, n) == (4, 5) else 4)}; absolute cap "
            f"{zbx.cap(d, n)}. Generic sampling and hill-climbing are already "
            "exhausted at the incumbent -- find structure, not a better random "
            "search."),
        "programLanguage": "PYTHON",
        "runSettings": {"maxPrograms": max_programs, "concurrency": concurrency,
                        "maxDuration": "21600s"},
        "generationSettings": {"context": context_text(d, n),
                               "includeFullProgramInPrompt": True,
                               "models": [{"name": "gemini-3.1-pro-preview",
                                           "weight": 1.0}]},
        "evolutionSettings": {"parentSamplingConfig": {"paretoSamplingConfig": {
            "paretoSamplingProbability": 0.3}}},
    }
    exp = A.create_experiment(session, cfg)["name"]
    print("experiment:", exp, flush=True)
    open(os.path.join(HERE, "_campaign.txt"), "w").write(exp)
    A.create_program(exp, [("main.py", seed_src)],
                     {"vertices": seed_res["vertices"],
                      "robustness": seed_res["robustness"]},
                     "incumbent: paper-faithful sampling + hill climb")
    A.start(exp)

    best, done, t0 = seed_res["vertices"], 0, time.time()
    try:
        while done < max_programs and time.time() - t0 < 6 * 3600:
            progs = A.acquire(exp, concurrency)
            if not progs:
                time.sleep(15)
                continue
            for p in progs:
                src = p["content"]["files"][0]["content"]
                res = evaluate(src, d, n)
                v = res["vertices"]
                note = ""
                if v >= incumbent and "instance" in res:
                    f0, cert = exact_gate(res["instance"], d, n, incumbent)
                    note = f" exact={f0}"
                    if cert:
                        path = os.path.join(HERE, f"record_{d}{n}_{f0}.json")
                        json.dump(cert, open(path, "w"), indent=1)
                        print("  *** RECORD", f0, ">", incumbent, "->", path,
                              flush=True)
                    elif f0 < v:
                        note += " (float count NOT confirmed exactly)"
                A.submit(exp, p["lockToken"], p["name"],
                         {"vertices": v, "robustness": res["robustness"]},
                         insights={"error": res["error"]} if res.get("error")
                         else None)
                done += 1
                best = max(best, v)
                st = A.stats(exp)
                usd = (int(st.get("inputTokenCount", 0)) * USD_IN
                       + int(st.get("outputTokenCount", 0)) * USD_OUT)
                print(f"[{done}/{max_programs}] v={v}{note} best={best} "
                      f"tok={st.get('inputTokenCount', 0)}/"
                      f"{st.get('outputTokenCount', 0)} ~${usd:.3f}", flush=True)
                if usd > max_usd:
                    print("COST CEILING HIT - stopping", flush=True)
                    return
    finally:
        A.delete_experiment(exp)
        print("experiment deleted; best =", best)


if __name__ == "__main__":
    main()
