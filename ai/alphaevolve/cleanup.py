"""Kill switch.  There is no :stop / :pause in v1alpha -- DELETE is the only way
to stop a started experiment, and a started experiment that nobody is polling
can still burn tokens against a 100M-token/day quota.

Run this after every session.  `python cleanup.py --engines` also deletes the
throwaway probe engine.
"""
import sys

import ae_api as A

ENGINES = ["finite-certificates-lit-search", "research-search",
           "alphaevolve-probe-app"]
PROBE_ENGINES = ["alphaevolve-probe-app"]      # created by this project only


def engine_path(e):
    return (f"projects/{A.PROJECT_NUMBER}/locations/global/collections/"
            f"default_collection/engines/{e}")


def main(drop_engines=False):
    for e in ENGINES:
        ep = engine_path(e)
        r = A.call("GET", f"{ep}/sessions", params={"pageSize": 100}, quiet=True)
        if not r.ok:
            print(f"{e}: no sessions ({r.status_code})")
            continue
        for s in r.json().get("sessions", []):
            sn = s["name"]
            r2 = A.call("GET", f"{sn}/alphaEvolveExperiments",
                        params={"pageSize": 100}, quiet=True)
            if not r2.ok:
                continue
            for x in r2.json().get("alphaEvolveExperiments", []):
                st = x.get("state")
                d = A.delete_experiment(x["name"])
                print(f"  deleted [{st}] {x['config'].get('title')} "
                      f"{x['name'].rsplit('/', 1)[-1]} -> {d.status_code}")
    if drop_engines:
        for e in PROBE_ENGINES:
            r = A.call("DELETE", engine_path(e), quiet=True)
            print(f"engine {e} -> {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    main("--engines" in sys.argv)
