"""Why does a STARTED experiment never produce candidates?  Bisect it cheaply.

Each variant caps maxPrograms at 3, so if generation DOES fire the exposure is
a couple of LLM calls.  Polls acquirePrograms and the stats counter.
"""
import copy
import json
import sys
import time

import ae_api as A

S = open("_session.txt").read().strip().replace(
    "projects/project-ebd5a273-53ea-4c8b-81a", "projects/159398774377")

SEED_MARKED = '''"""Toy: return a list of 20 bits.  Score = number of ones."""


# EVOLVE-BLOCK-START
def build():
    return [0] * 20
# EVOLVE-BLOCK-END
'''

SEED_PLAIN = '''"""Toy: return a list of 20 bits.  Score = number of ones."""


def build():
    return [0] * 20
'''

BASE = {
    "title": "probe",
    "problemDescription": ("Write build() returning a Python list of exactly 20 "
                           "integers, each 0 or 1. Score = number of 1s. "
                           "Maximise it (best 20)."),
    "programLanguage": "PYTHON",
    "runSettings": {"maxPrograms": 3, "concurrency": 2, "maxDuration": "3600s"},
}

VARIANTS = {}
VARIANTS["A_default_model_marked"] = (copy.deepcopy(BASE), SEED_MARKED)
c = copy.deepcopy(BASE)
VARIANTS["B_default_model_plain"] = (c, SEED_PLAIN)
c = copy.deepcopy(BASE)
c["generationSettings"] = {"models": [{"name": "gemini-3.1-pro-preview",
                                       "weight": 1.0}],
                           "includeFullProgramInPrompt": True}
VARIANTS["C_pro_model_marked"] = (c, SEED_MARKED)


def main(names, minutes=8):
    live = {}
    for nm in names:
        cfg, seed = VARIANTS[nm]
        cfg = copy.deepcopy(cfg)
        cfg["title"] = nm
        exp = A.create_experiment(S, cfg)["name"]
        A.create_program(exp, [("main.py", seed)], {"ones": 0.0}, "seed")
        A.start(exp)
        live[nm] = exp
        print(nm, "->", exp.rsplit("/", 1)[-1], flush=True)

    t0 = time.time()
    while time.time() - t0 < minutes * 60:
        time.sleep(20)
        allq = True
        for nm, exp in live.items():
            progs = A.acquire(exp, 2)
            st = A.stats(exp)
            print(f"  [{time.time()-t0:5.0f}s] {nm}: acquired {len(progs)} "
                  f"stats={json.dumps(st)}", flush=True)
            if progs:
                allq = False
                for p in progs:
                    src = p["content"]["files"][0]["content"]
                    print("   --- generated program ---")
                    print(src[:1500])
                    g = {}
                    try:
                        exec(src, g)
                        sc = float(sum(1 for x in g["build"]() if x == 1))
                    except Exception as e:                        # noqa: BLE001
                        sc = 0.0
                        print("   eval error", e)
                    A.submit(exp, p["lockToken"], p["name"], {"ones": sc})
                    print("   submitted score", sc)
            if st.get("candidatesCount", 1) > 1:
                allq = False
        if not allq:
            print("GENERATION CONFIRMED", flush=True)
    for nm, exp in live.items():
        print(nm, "final:", json.dumps(A.get_experiment(exp).get("stats", {})),
              A.get_experiment(exp).get("state"))
        open("_variants.txt", "a").write(nm + " " + exp + "\n")


if __name__ == "__main__":
    main(sys.argv[1:] or list(VARIANTS), minutes=8)
