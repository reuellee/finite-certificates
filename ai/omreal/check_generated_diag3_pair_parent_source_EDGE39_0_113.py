#!/usr/bin/env python3
"""Producer-side self-consistency check for already-generated edge-39 artifacts.

This is deliberately not an independent acceptance verifier: it imports the
generator core.  The independent verifier track must embody its own parser and
mathematical checks.
"""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_labels_EDGE39_0_113_core as labels  # noqa: E402
import diag3_pair_parent_source_transition_EDGE39_0_113_core as transition  # noqa: E402


def main():
    transition_record = json.loads(transition.OUTPUT.read_text(encoding="utf-8"))
    if transition_record["semantic_sha256"] != transition.semantic_seal(transition_record):
        raise AssertionError("transition semantic seal failed")
    label_record = json.loads(labels.OUTPUT.read_text(encoding="utf-8"))
    if label_record["semantic_sha256"] != transition.semantic_seal(label_record):
        raise AssertionError("label semantic seal failed")
    if label_record["inputs"]["transition_sha256"] != labels.file_sha256(transition.OUTPUT):
        raise AssertionError("label/transition raw digest cross-pin failed")
    result = labels.check_profile_artifact(
        labels.PROFILE_OUTPUT,
        label_record["signature_profiles"]["semantic_sha256"],
    )
    if label_record["signature_profiles"]["artifact_sha256"] != labels.file_sha256(labels.PROFILE_OUTPUT):
        raise AssertionError("packed profile raw digest cross-pin failed")
    print("PASS producer-side edge-39 semantic seals and cross-pins")
    print("PASS packed profiles", result)


if __name__ == "__main__":
    main()
