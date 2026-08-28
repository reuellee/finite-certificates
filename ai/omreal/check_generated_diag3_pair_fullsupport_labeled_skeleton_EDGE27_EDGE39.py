#!/usr/bin/env python3
"""Producer-side self-check for the generated edge-27/edge-39 skeleton.

This imports the producer core and is not an independent verification gate.
"""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_fullsupport_labeled_skeleton_EDGE27_EDGE39_core as core  # noqa: E402


def main():
    core.require_pins()
    record = json.loads(core.OUTPUT.read_text(encoding="utf-8"))
    if record["semantic_sha256"] != core.semantic_seal(record):
        raise AssertionError("combined skeleton semantic seal failed")
    core.validate_record(record)
    expected_raw = record["joint_signature_profiles"]["artifact_sha256"]
    if core.file_sha256(core.PROFILE_OUTPUT) != expected_raw:
        raise AssertionError("combined profile artifact raw digest changed")
    header = core.check_profile_artifact(core.PROFILE_OUTPUT, record)
    print("PASS combined edge-27/edge-39 regular-CW tree", record["compiled_regular_subcomplex"]["cell_count_by_dimension"])
    print("PASS combined joint bad-membership profiles", header)
    print("PASS collar attachment", record["collar_attachment"]["edge_event_cell"], "-> w_zero")


if __name__ == "__main__":
    main()
