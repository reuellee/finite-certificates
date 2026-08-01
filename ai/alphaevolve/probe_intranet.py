"""Test 2: does AlphaEvolve generate when the experiment hangs off a Gemini
Enterprise (APP_TYPE_INTRANET) engine with requiredSubscriptionTier set?

Capped at 3 programs.  The engine is deleted by cleanup.py afterwards.
"""
import json
import time

import ae_api as A

SESSION = ("projects/159398774377/locations/global/collections/"
           "default_collection/engines/alphaevolve-probe-app/sessions/"
           "582053580630377742")

SEED = '''"""Toy: return a list of 20 bits.  Score = number of ones."""


# EVOLVE-BLOCK-START
def build():
    return [0] * 20
# EVOLVE-BLOCK-END
'''

CFG = {
    "title": "probe-intranet",
    "problemDescription": ("Write build() returning a Python list of exactly 20 "
                           "integers, each 0 or 1. Score = number of 1s. "
                           "Maximise it (best 20)."),
    "programLanguage": "PYTHON",
    "runSettings": {"maxPrograms": 3, "concurrency": 2, "maxDuration": "1800s"},
    "generationSettings": {"includeFullProgramInPrompt": True,
                           "models": [{"name": "gemini-3.1-pro-preview",
                                       "weight": 1.0}]},
}

exp = A.create_experiment(SESSION, CFG)["name"]
print("exp", exp, flush=True)
open("_intranet.txt", "w").write(exp)
A.create_program(exp, [("main.py", SEED)], {"ones": 0.0}, "seed")
print("start", json.dumps(A.start(exp))[:200], flush=True)

t0 = time.time()
while time.time() - t0 < 600:
    time.sleep(20)
    progs = A.acquire(exp, 2)
    st = A.stats(exp)
    print(f"[{time.time()-t0:5.0f}s] acquired {len(progs)} stats={json.dumps(st)}",
          flush=True)
    for p in progs:
        src = p["content"]["files"][0]["content"]
        print("--- GENERATED ---\n" + src[:1200], flush=True)
        g = {}
        try:
            exec(src, g)
            sc = float(sum(1 for x in g["build"]() if x == 1))
        except Exception as e:                                   # noqa: BLE001
            sc = 0.0
        A.submit(exp, p["lockToken"], p["name"], {"ones": sc})
        print("  scored", sc, flush=True)
    if st.get("candidatesCount", 1) > 1:
        print("GENERATION CONFIRMED", flush=True)
print("final", json.dumps(A.get_experiment(exp).get("stats", {})),
      A.get_experiment(exp).get("state"))
