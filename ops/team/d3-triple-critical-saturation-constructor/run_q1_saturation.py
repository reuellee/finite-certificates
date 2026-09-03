#!/usr/bin/env python3
"""Guarded sequential Singular runner for the conditional Q1 saturation.

Dry-run and smoke-test modes are Q0-safe.  The real 62-stage job refuses to
start unless supplied an independent acceptance artifact bound to the exact
contract bytes and semantic digest.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT = HERE / "SATURATION_CONTRACT.json"
SYSTEM = ROOT / "ai" / "omreal" / "data" / "DIAG3_triple_fullspace_critical_h1.json"
WSL_DISTRO = "lee-dev"
SINGULAR = "/home/lee/.local/share/9dvl-exact-cas/v1/bin/Singular"
VARIABLES = tuple("abcdefghi")
STAGE_TIMEOUT_SECONDS = 180
TOTAL_TIMEOUT_SECONDS = 12_600
ADDRESS_SPACE_LIMIT_BYTES = 7 * (1 << 30)


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def validate_contract() -> tuple[dict, dict]:
    contract = json.loads(CONTRACT.read_text(encoding="ascii"))
    system = json.loads(SYSTEM.read_text(encoding="ascii"))
    semantic = dict(contract)
    stored = semantic.pop("semantic_sha256")
    require(canonical_digest(semantic) == stored, "contract semantic digest")
    source = contract["source_ideal"]
    require(digest_path(SYSTEM) == source["artifact_sha256"], "source bytes")
    require(canonical_digest(system) == source["artifact_semantic_sha256"], "source semantic")
    require(contract["saturation_contract"]["ordered"] is True, "ordered contract")
    require(
        contract["saturation_contract"]["anonymous_product_saturation_used"] is False,
        "anonymous saturation",
    )
    stages = contract["saturation_contract"]["stages"]
    require(len(stages) == 62, "stage count")
    require([stage["stage_index"] for stage in stages] == list(range(62)), "stage order")
    require(contract["q0_disposition"]["q1_status"].startswith("DENIED"), "unguarded Q1")
    return contract, system


def validate_acceptance(path: Path, contract: dict) -> dict:
    acceptance = json.loads(path.read_text(encoding="utf-8"))
    require(acceptance.get("accepted") is True, "Q0 acceptance flag")
    require(acceptance.get("verdict") == "ACCEPT", "Q0 acceptance verdict")
    require(acceptance.get("q0_status") == "ACCEPTED", "Q0 acceptance status")
    require(acceptance.get("independent_verifier") is True, "Q0 independence")
    require(acceptance.get("contract_sha256") == digest_path(CONTRACT), "accepted contract bytes")
    require(
        acceptance.get("contract_semantic_sha256") == contract["semantic_sha256"],
        "accepted contract semantic",
    )
    return acceptance


def singular_polynomial(terms: list[list]) -> str:
    require(bool(terms), "zero polynomial cannot be emitted as a generator")
    pieces: list[tuple[int, str]] = []
    for coefficient, exponents in terms:
        require(len(exponents) == 9, "polynomial arity")
        factors = []
        for variable, exponent in zip(VARIABLES, exponents, strict=True):
            if exponent == 1:
                factors.append(variable)
            elif exponent > 1:
                factors.append(f"{variable}^{exponent}")
        absolute = abs(int(coefficient))
        if factors:
            monomial = "*".join(factors)
            body = monomial if absolute == 1 else f"{absolute}*{monomial}"
        else:
            body = str(absolute)
        pieces.append((1 if coefficient > 0 else -1, body))
    output = ""
    for index, (sign, body) in enumerate(pieces):
        if index == 0:
            output += body if sign > 0 else f"-{body}"
        else:
            output += ("+" if sign > 0 else "-") + body
    return output


def wsl_path(path: Path) -> str:
    completed = subprocess.run(
        ["wsl.exe", "-d", WSL_DISTRO, "--", "wslpath", "-a", str(path.resolve())],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def run_singular(script: Path, timing: Path, timeout_seconds: int) -> subprocess.CompletedProcess:
    linux_script = wsl_path(script)
    linux_timing = wsl_path(timing)
    launcher = script.with_suffix(".launcher.py")
    launcher.write_text(
        "import resource\n"
        "import subprocess\n"
        "import sys\n"
        "import time\n"
        "start=time.perf_counter()\n"
        f"completed=subprocess.run([{SINGULAR!r},'-q',sys.argv[1]])\n"
        "usage=resource.getrusage(resource.RUSAGE_CHILDREN)\n"
        "with open(sys.argv[2],'w',encoding='ascii') as target:\n"
        " target.write(f'elapsed_seconds={time.perf_counter()-start:.6f}\\n')\n"
        " target.write(f'maximum_resident_set_kib={usage.ru_maxrss}\\n')\n"
        "raise SystemExit(completed.returncode)\n",
        encoding="ascii",
    )
    linux_launcher = wsl_path(launcher)
    command = (
        f"timeout {timeout_seconds}s "
        f"prlimit --as={ADDRESS_SPACE_LIMIT_BYTES} -- "
        f"python3 {shlex.quote(linux_launcher)} "
        f"{shlex.quote(linux_script)} {shlex.quote(linux_timing)}"
    )
    return subprocess.run(
        ["wsl.exe", "-d", WSL_DISTRO, "--", "bash", "-lc", command],
        text=True,
        capture_output=True,
        timeout=timeout_seconds + 20,
    )


def smoke_test() -> None:
    smoke_parent = ROOT.parent / "outputs"
    smoke_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="d3-q0-singular-smoke-", dir=smoke_parent
    ) as directory:
        root = Path(directory)
        script = root / "smoke.sing"
        timing = root / "smoke.time"
        script.write_text(
            'LIB "elim.lib";\n'
            'ring R=0,(x,y),dp;\n'
            'ideal I=x2,xy;\n'
            'list L=sat_with_exp(I,ideal(x));\n'
            'ideal J=L[1];\n'
            'print("Q0_SMOKE|"+string(L[2])+"|"+string(size(J)));\n'
            'quit;\n',
            encoding="ascii",
        )
        completed = run_singular(script, timing, 30)
        require(completed.returncode == 0, f"Singular smoke return {completed.returncode}")
        require("Q0_SMOKE|" in completed.stdout, "Singular smoke marker")
        print(completed.stdout.strip())
        print("PASS guarded Singular sat_with_exp smoke test")


def initial_stage_script(system: dict, stage: dict, next_state: str, metadata: str) -> str:
    generators = [
        singular_polynomial(equation["terms"])
        for equation in system["equations"]
        if equation["terms"]
    ]
    return stage_script_body(
        'ring R=0,(a,b,c,d,e,f,g,h,i),dp;\nideal J=' + ",\n".join(generators) + ";\n",
        stage,
        next_state,
        metadata,
    )


def continuation_stage_script(previous_state: str, stage: dict, next_state: str, metadata: str) -> str:
    prefix = f'execute(read("{previous_state}"));\n'
    return stage_script_body(prefix, stage, next_state, metadata)


def stage_script_body(prefix: str, stage: dict, next_state: str, metadata: str) -> str:
    factor = singular_polynomial(stage["sparse_polynomial"])
    index = stage["stage_index"]
    label = stage["parent_bracket_label"]
    return (
        prefix
        + 'LIB "elim.lib";\n'
        + "option(redSB);\n"
        + f"poly H={factor};\n"
        + "list L=sat_with_exp(J,ideal(H));\n"
        + "J=L[1];\n"
        + "int saturation_exponent=L[2];\n"
        + f'write("{metadata}","stage={index};label={label};exponent="'
        + '+string(saturation_exponent)+";basis_size="+string(size(J)));\n'
        + f'print("Q1_STAGE|{index}|{label}|"+string(saturation_exponent)+"|"+string(size(J)));\n'
        + "kill H; kill L; kill saturation_exponent;\n"
        + f'dump("{next_state}");\n'
        + "quit;\n"
    )


def peak_rss_kib(timing: Path) -> int | None:
    if not timing.exists():
        return None
    match = re.search(
        r"maximum_resident_set_kib=(\d+)",
        timing.read_text(encoding="utf-8", errors="replace"),
    )
    return int(match.group(1)) if match else None


def write_frontier(scratch: Path, value: dict) -> None:
    (scratch / "RUN_FRONTIER.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )


def execute_job(contract: dict, system: dict, acceptance: dict, scratch: Path) -> None:
    scratch = scratch.resolve()
    scratch.mkdir(parents=True, exist_ok=False)
    stages = contract["saturation_contract"]["stages"]
    completed_stages = []
    elapsed_budget = 0
    previous_state: Path | None = None
    for stage in stages:
        index = stage["stage_index"]
        script = scratch / f"stage_{index:02d}.sing"
        timing = scratch / f"stage_{index:02d}.time"
        metadata = scratch / f"stage_{index:02d}.txt"
        next_state = scratch / f"state_{index + 1:02d}.sing"
        linux_next = wsl_path(next_state).replace('"', '\\"')
        linux_meta = wsl_path(metadata).replace('"', '\\"')
        if previous_state is None:
            source = initial_stage_script(system, stage, linux_next, linux_meta)
        else:
            linux_previous = wsl_path(previous_state).replace('"', '\\"')
            source = continuation_stage_script(
                linux_previous, stage, linux_next, linux_meta
            )
        script.write_text(source, encoding="ascii")
        completed = run_singular(script, timing, STAGE_TIMEOUT_SECONDS)
        elapsed_budget += STAGE_TIMEOUT_SECONDS
        record = {
            "stage_index": index,
            "parent_bracket_label": stage["parent_bracket_label"],
            "return_code": completed.returncode,
            "peak_rss_kib": peak_rss_kib(timing),
            "stdout": completed.stdout[-4_000:],
            "stderr": completed.stderr[-4_000:],
            "state_sha256": digest_path(next_state) if next_state.exists() else None,
        }
        completed_stages.append(record)
        if completed.returncode != 0 or not next_state.exists():
            write_frontier(
                scratch,
                {
                    "status": "TIMEOUT" if completed.returncode == 124 else "ERROR",
                    "last_completed_stage": index - 1,
                    "failed_stage": index,
                    "records": completed_stages,
                    "q1_consequence": "NONE",
                    "theorem_ledger": "2/9",
                    "triple_source_residual": 1_162_302,
                },
            )
            raise SystemExit(completed.returncode or 1)
        previous_state = next_state
        if elapsed_budget >= TOTAL_TIMEOUT_SECONDS:
            write_frontier(
                scratch,
                {
                    "status": "TIMEOUT",
                    "last_completed_stage": index,
                    "failed_stage": None,
                    "records": completed_stages,
                    "q1_consequence": "NONE",
                    "theorem_ledger": "2/9",
                    "triple_source_residual": 1_162_302,
                },
            )
            raise SystemExit(124)
    write_frontier(
        scratch,
        {
            "status": "SATURATION_COMPLETE_Q1_STILL_REQUIRES_DIMENSION_REAL_ROOT_AND_ATTACHMENT_CHECKS",
            "last_completed_stage": 61,
            "final_state_sha256": digest_path(previous_state),
            "records": completed_stages,
            "acceptance_sha256": canonical_digest(acceptance),
            "q1_consequence": "NONE_PENDING_REMAINING_Q1_OBLIGATIONS",
            "theorem_ledger": "2/9",
            "triple_source_residual": 1_162_302,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--smoke-test", action="store_true")
    group.add_argument("--execute", action="store_true")
    parser.add_argument("--acceptance", type=Path)
    parser.add_argument("--scratch", type=Path)
    arguments = parser.parse_args()

    contract, system = validate_contract()
    if arguments.dry_run:
        print("PASS exact contract and source binding")
        print("STAGES", len(contract["saturation_contract"]["stages"]))
        print("BACKEND", WSL_DISTRO, SINGULAR, "sat_with_exp")
        print("LIMITS", STAGE_TIMEOUT_SECONDS, TOTAL_TIMEOUT_SECONDS, ADDRESS_SPACE_LIMIT_BYTES)
        print("Q1 DENIED without independent acceptance")
        return
    if arguments.smoke_test:
        smoke_test()
        print("Q1 DENIED; smoke test used only a toy ideal")
        return

    require(arguments.acceptance is not None, "missing independent acceptance")
    require(arguments.scratch is not None, "missing scratch directory")
    acceptance = validate_acceptance(arguments.acceptance, contract)
    execute_job(contract, system, acceptance, arguments.scratch)


if __name__ == "__main__":
    main()
