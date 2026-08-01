"""End-to-end smoke test of the AlphaEvolve API on a 3-line toy problem.

Purpose: prove create -> seed -> start -> acquire -> evaluate -> submit -> list
closes, and pin the exact payloads, BEFORE any real evaluator exists.
Toy objective: return a 20-bit list with as many 1s as possible (max 20).

Usage: python probe_toy.py [maxPrograms]
"""
import json
import os
import sys
import time

import ae_api as A

SESSION = A.session_path(os.environ.get("AE_SESSION", "851551224574743065"))

SEED = '''"""Toy: return a list of 20 bits.  Score = number of ones."""


# EVOLVE-BLOCK-START
def build():
    return [0] * 20
# EVOLVE-BLOCK-END
'''

CONFIG = {
    "title": "probe-popcount",
    "problemDescription": (
        "Write build() returning a Python list of exactly 20 integers, each 0 "
        "or 1. The score is the number of 1s. Maximise it (best possible 20)."),
    "programLanguage": "PYTHON",
    "runSettings": {"maxPrograms": int(sys.argv[1]) if len(sys.argv) > 1 else 4,
                    "concurrency": 1, "maxDuration": "1200s"},
    "generationSettings": {
        "context": "Return the list directly; no imports needed.",
        "includeFullProgramInPrompt": True,
        "models": [{"name": "gemini-3.1-pro-preview", "weight": 1.0}]},
    "evolutionSettings": {"parentSamplingConfig": {
        "paretoSamplingConfig": {"paretoSamplingProbability": 0.0}}},
}


def evaluate(src):
    g = {}
    try:
        exec(src, g)
        v = g["build"]()
        return float(sum(1 for x in v if x == 1)), None
    except Exception as e:                                   # noqa: BLE001
        return 0.0, repr(e)


def main():
    exp = A.create_experiment(SESSION, CONFIG)
    name = exp["name"]
    print("experiment:", name)
    print(json.dumps(exp, indent=1)[:800])

    s0, e0 = evaluate(SEED)
    seed = A.create_program(name, [("main.py", SEED)], {"ones": s0},
                            "seed: all zeros")
    print("seed program:", seed.get("name"), "score", s0)

    print("start ->", json.dumps(A.start(name))[:300])

    done = 0
    t0 = time.time()
    while done < CONFIG["runSettings"]["maxPrograms"] and time.time() - t0 < 900:
        progs = A.acquire(name, 1)
        if not progs:
            time.sleep(6)
            continue
        for p in progs:
            src = p["content"]["files"][0]["content"]
            score, err = evaluate(src)
            print(f"  [{done}] {p['name'].rsplit('/', 1)[-1]} -> {score}"
                  + (f"  ERR {err}" if err else ""))
            A.submit(name, p["lockToken"], p["name"], {"ones": score},
                     insights={"error": err} if err else None)
            done += 1

    time.sleep(5)
    lst = A.list_programs(name, state="COMPLETED", order_by="ones desc")
    print("\nCOMPLETED programs:", len(lst.get("alphaEvolvePrograms", [])))
    for p in lst.get("alphaEvolvePrograms", []):
        sc = p.get("evaluation", {}).get("scores", {}).get("scores", [])
        print("  ", p["name"].rsplit("/", 1)[-1], sc)
    print("\nstats:", json.dumps(A.stats(name), indent=1))
    print("experiment state:", A.get_experiment(name).get("state"))
    open("_probe_experiment.txt", "w").write(name)


if __name__ == "__main__":
    main()
