#!/usr/bin/env python3
"""Compile and run the exact support-drop low-source and minimality census."""

from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "verify_diag2_generic_birth_support_filter.cpp"


def main():
    with tempfile.TemporaryDirectory(prefix="diag2-support-drop-") as build:
        executable = Path(build) / "verify_diag2_generic_birth_support_filter"
        command = [
            "g++",
            "-std=c++17",
            "-O3",
            str(SOURCE),
            "-o",
            str(executable),
        ]
        compiled = subprocess.run(command, capture_output=True, text=True, check=False)
        if compiled.returncode:
            raise RuntimeError("failed to compile support-drop census:\n" + compiled.stderr)
        completed = subprocess.run(
            [str(executable)], capture_output=True, text=True, check=False
        )
        if completed.returncode:
            raise RuntimeError("support-drop census failed:\n" + completed.stderr)
        print(completed.stdout, end="")


if __name__ == "__main__":
    main()
