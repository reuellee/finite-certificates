"""Last config lever: a larger maxPrograms / concurrency, and the quota header
set to the project NUMBER rather than the project ID.  Capped at 20 programs.
"""
import json
import time

import ae_api as A

A.PROJECT = "159398774377"          # x-goog-user-project as the project number

SEED = '''"""Toy: return a list of 20 bits.  Score = number of ones."""


# EVOLVE-BLOCK-START
def build():
    return [0] * 20
# EVOLVE-BLOCK-END
'''

CFG = {
    "title": "probe-bigger",
    "problemDescription": ("Write build() returning a Python list of exactly 20 "
                           "integers, each 0 or 1. Score = number of 1s. "
                           "Maximise it (best 20)."),
    "programLanguage": "PYTHON",
    "runSettings": {"maxPrograms": 20, "concurrency": 4, "maxDuration": "3600s"},
    "generationSettings": {"includeFullProgramInPrompt": True,
                           "models": [{"name": "gemini-3.1-pro-preview",
                                       "weight": 1.0}]},
    "evolutionSettings": {"parentSamplingConfig": {
        "paretoSamplingConfig": {"paretoSamplingProbability": 0.3}}},
}

S = A.session_path("851551224574743065")
exp = A.create_experiment(S, CFG)["name"]
print("exp", exp, flush=True)
A.create_program(exp, [("main.py", SEED)], {"ones": 0.0}, "seed")
print("start", json.dumps(A.start(exp))[:200], flush=True)
open("_bigger.txt", "w").write(exp)

t0 = time.time()
done = 0
while time.time() - t0 < 900 and done < 20:
    time.sleep(20)
    progs = A.acquire(exp, 4)
    st = A.stats(exp)
    print(f"[{time.time()-t0:5.0f}s] acquired {len(progs)} stats={json.dumps(st)}",
          flush=True)
    for p in progs:
        src = p["content"]["files"][0]["content"]
        g = {}
        try:
            exec(src, g)
            sc = float(sum(1 for x in g["build"]() if x == 1))
        except Exception as e:                                   # noqa: BLE001
            sc = 0.0
            print("  eval error", e)
        A.submit(exp, p["lockToken"], p["name"], {"ones": sc})
        done += 1
        print("  scored", sc, flush=True)
    if st.get("inputTokenCount"):
        print("TOKENS SEEN:", json.dumps(st), flush=True)
print("final", json.dumps(A.get_experiment(exp).get("stats", {})),
      A.get_experiment(exp).get("state"))
