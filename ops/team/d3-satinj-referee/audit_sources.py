#!/usr/bin/env python3
"""Independent source pin replay; imports no producer code."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

BASE = "3a7ce7b5d57543d54eace7707659418cea6d69c9"
TREE = "7e2e958bcc7fef306bfc309c1502a279925b4ab6"
CYCLE = "ops/research-team/cycles/2026-09-09-saturation-injectivity"
EXTRA = [
    "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1/CYCLE_REPORT.md",
    "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/CYCLE_REPORT.md",
    "ops/research-team/cycles/2026-09-09-backward-detector/CYCLE_REPORT.md",
]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--opening-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    manifest_bytes = (args.opening_root / CYCLE / "SOURCE_MANIFEST.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["base_revision"] == BASE
    assert manifest["base_tree"] == TREE
    assert git(root, "rev-parse", BASE + "^{tree}").decode().strip() == TREE
    source_pins = {}
    for path, expected in manifest["inputs"].items():
        data = (root / path).read_bytes()
        assert digest(data) == expected, path
        assert git(root, "show", BASE + ":" + path) == data, path
        source_pins[path] = expected
    for path in EXTRA:
        data = (root / path).read_bytes()
        assert git(root, "show", BASE + ":" + path) == data, path
        source_pins[path] = digest(data)
    closing = json.loads((root / "ops/research-team/cycles/2026-09-09-backward-detector/CLOSING_STATE.json").read_bytes())
    assert closing["ledger"] == "2/9"
    assert closing["closing_proof_distance"] == ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 12, 15]
    assert set(closing["open_obligations"].values()) == {"INCONCLUSIVE"}
    opening_pins = {}
    for name in ["SOURCE_MANIFEST.json", "CYCLE.md", "WORK_ORDERS.yaml"]:
        data = (args.opening_root / CYCLE / name).read_bytes()
        opening_pins[CYCLE + "/" + name] = digest(data)
    result = {
        "verdict": "PASS_SOURCE_PINS_AND_INHERITED_STATE",
        "base_revision": BASE,
        "base_tree": TREE,
        "manifest_input_count": len(manifest["inputs"]),
        "additional_source_count": len(EXTRA),
        "source_pins": source_pins,
        "opening_pins": opening_pins,
        "opening_proof_distance": closing["closing_proof_distance"],
        "producer_artifacts_read": False,
        "producer_imports": [],
        "scope": "Repository source identity and inherited theorem state; no archive-byte or remote-head verification is asserted by this replay.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")

if __name__ == "__main__":
    main()
