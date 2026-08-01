"""Thin client for the Discovery Engine AlphaEvolve API (v1alpha).

Reusable asset: every call this project needs, with the exact headers and
paths that were verified to work.  See API_NOTES.md for the payloads.

Auth: `gcloud auth print-access-token` + the x-goog-user-project header
(the project must be the one holding the Gemini Enterprise licence).
"""
import json
import os
import subprocess
import time

import requests

PROJECT = os.environ.get("AE_PROJECT", "project-ebd5a273-53ea-4c8b-81a")
# GOTCHA (verified 2026-08-01): alphaEvolveExperiments.create rejects a
# resource path built on the project ID with a bare INVALID_ARGUMENT and no
# field violations.  The project NUMBER works.  Sessions accept either, so the
# failure looks like a config problem until you swap this.
PROJECT_NUMBER = os.environ.get("AE_PROJECT_NUMBER", "159398774377")
ENGINE = os.environ.get("AE_ENGINE", "finite-certificates-lit-search")
LOCATION = "global"
COLLECTION = "default_collection"
BASE = "https://discoveryengine.googleapis.com/v1alpha"

ENGINE_PATH = (f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/"
               f"{COLLECTION}/engines/{ENGINE}")

_TOKEN = {"value": None, "t": 0.0}

# On Windows `gcloud` is a .cmd shim; subprocess needs the explicit file.
_GCLOUD = os.environ.get("AE_GCLOUD") or (
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk"
                       r"\bin\gcloud.cmd") if os.name == "nt" else "gcloud")


def token(force=False):
    if force or _TOKEN["value"] is None or time.time() - _TOKEN["t"] > 1800:
        _TOKEN["value"] = subprocess.run(
            [_GCLOUD, "auth", "print-access-token"],
            capture_output=True, text=True, check=True).stdout.strip()
        _TOKEN["t"] = time.time()
    return _TOKEN["value"]


def headers():
    return {"Authorization": f"Bearer {token()}",
            "x-goog-user-project": PROJECT,
            "Content-Type": "application/json"}


def call(method, path, body=None, params=None, quiet=False, retries=3):
    url = path if path.startswith("http") else f"{BASE}/{path}"
    last = None
    for attempt in range(retries):
        r = requests.request(method, url, headers=headers(), json=body,
                             params=params, timeout=180)
        if r.status_code == 401:          # token expired
            token(force=True)
            continue
        if r.status_code in (429, 500, 503) and attempt + 1 < retries:
            time.sleep(2 ** attempt * 3)
            last = r
            continue
        if not r.ok and not quiet:
            raise RuntimeError(f"{method} {url} -> {r.status_code}\n{r.text}")
        return r
    return last


def session_path(session_id):
    return f"{ENGINE_PATH}/sessions/{session_id}"


# ---------------------------------------------------------------- sessions
def create_session(display_name="alphaevolve"):
    r = call("POST", f"{ENGINE_PATH}/sessions",
             {"displayName": display_name, "state": "IN_PROGRESS"})
    return r.json()["name"]


def list_sessions():
    return call("GET", f"{ENGINE_PATH}/sessions").json()


# ------------------------------------------------------------- experiments
def create_experiment(session, config):
    """session: full resource name .../sessions/{id}.  Returns experiment dict."""
    r = call("POST", f"{session}/alphaEvolveExperiments", {"config": config})
    return r.json()


def get_experiment(experiment):
    return call("GET", experiment).json()


def list_experiments(session):
    return call("GET", f"{session}/alphaEvolveExperiments").json()


def delete_experiment(experiment):
    return call("DELETE", experiment, quiet=True)


def create_program(experiment, files, scores, description="", insights=None):
    """Seed program.  files: list of (path, content).  Call BEFORE :start.

    `scores` is REQUIRED: the service rejects a seed with no evaluation
    ("evaluation_results.scores must contain at least one score").  Evaluate
    the seed locally first and pass its real scores -- they become the
    baseline the first generation is compared against.
    """
    body = {"content": {
        "description": description,
        "files": [{"path": p, "content": c, "programLanguage": "PYTHON"}
                  for p, c in files]},
        "evaluation": {"scores": {"scores": [
            {"metric": k, "score": float(v)} for k, v in scores.items()]}}}
    if insights:
        body["evaluation"]["insights"] = {"insights": [
            {"label": k, "text": str(v)[:4000]} for k, v in insights.items()]}
    return call("POST", f"{experiment}/alphaEvolvePrograms", body).json()


def start(experiment):
    """StartExperimentRequest has only `name`; the body may be {}."""
    return call("POST", f"{experiment}:start", {"name": experiment}).json()


def resume(experiment):
    return call("POST", f"{experiment}:resume", {}).json()


def acquire(experiment, desired=1):
    """desiredProgramsCount goes in the BODY, not the query string."""
    r = call("POST", f"{experiment}:acquirePrograms",
             {"desiredProgramsCount": int(desired)})
    return r.json().get("programs", [])


def submit(experiment, lock_token, program, scores, insights=None):
    """scores: dict metric -> float.  insights: dict label -> text (optional).

    Only ONE submission per call is supported by the service.
    """
    ev = {"scores": {"scores": [{"metric": k, "score": float(v)}
                                for k, v in scores.items()]}}
    if insights:
        ev["insights"] = {"insights": [{"label": k, "text": str(v)[:4000]}
                                       for k, v in insights.items()]}
    body = {"evaluationSubmissions": [
        {"program": program, "lockToken": lock_token, "evaluation": ev}]}
    return call("POST", f"{experiment}:submitProgramsEvaluations", body).json()


def list_programs(experiment, state="COMPLETED", order_by=None, page_size=50,
                  page_token=None):
    p = {"pageSize": page_size}
    if state:
        p["stateFilter"] = state
    if order_by:
        p["orderBy"] = order_by
    if page_token:
        p["pageToken"] = page_token
    return call("GET", f"{experiment}/alphaEvolvePrograms", params=p).json()


def stats(experiment):
    """Same-session token accounting: candidatesCount / input+outputTokenCount."""
    return get_experiment(experiment).get("stats", {})


if __name__ == "__main__":
    import sys
    print(json.dumps(call("GET", sys.argv[1]).json(), indent=2)[:4000])
