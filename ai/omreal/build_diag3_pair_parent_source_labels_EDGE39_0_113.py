#!/usr/bin/env python3
"""Generate edge-39 label summary and deterministic packed profiles."""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_labels_EDGE39_0_113_core as core  # noqa: E402
import diag3_pair_parent_source_transition_EDGE39_0_113_core as transition_core  # noqa: E402


def main():
    record, universe, profiles = core.build_record(progress=True)
    core.write_profile_artifact(core.PROFILE_OUTPUT, universe, profiles, record["scope"]["generic_chambers"])
    core.check_profile_artifact(
        core.PROFILE_OUTPUT, record["signature_profiles"]["semantic_sha256"]
    )
    record["signature_profiles"]["artifact_sha256"] = core.file_sha256(core.PROFILE_OUTPUT)
    record["semantic_sha256"] = transition_core.semantic_seal(record)
    core.OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("WROTE", core.OUTPUT)
    print("WROTE", core.PROFILE_OUTPUT)


if __name__ == "__main__":
    main()
