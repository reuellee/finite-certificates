#!/usr/bin/env python3
"""Build the deterministic combined edge-27/edge-39 labelled skeleton."""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_fullsupport_labeled_skeleton_EDGE27_EDGE39_core as core  # noqa: E402


def main():
    record, universe, catalog = core.build_record(progress=True)
    core.write_profile_artifact(core.PROFILE_OUTPUT, universe, catalog)
    record["joint_signature_profiles"]["artifact_sha256"] = core.file_sha256(core.PROFILE_OUTPUT)
    record["semantic_sha256"] = core.semantic_seal(record)
    core.OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    core.check_profile_artifact(core.PROFILE_OUTPUT, record)
    print("WROTE", core.OUTPUT)
    print("WROTE", core.PROFILE_OUTPUT)


if __name__ == "__main__":
    main()
