#!/usr/bin/env python3
"""Run every verify_*.py in the tree; exit nonzero if any fails.

--fast skips the slow verifiers, including the expensive diagonal-two
atlases, canonical-edge, mutation-square, separator, and saturation replays.

--ci-delegated skips only verifiers that the required GitHub workflow runs in
their own jobs.  With no flag this script continues to run every verifier.
"""
import os, subprocess, sys

SLOW = {
    "verify_diag2_canonical_robust_edges.py",
    "verify_diag2_escape_minimal_separators.py",
    "verify_diag2_near_counterexample_atlas.py",
    "verify_diag2_near_counterexample_separators.py",
    "verify_diag2_singleton_four_obstruction.py",
    "verify_diag2_escape_set_atlas178.py",
    "verify_diag2_escape_set_mutation_square.py",
    "verify_diag2_extremal_coordinate_survey.py",
    "verify_diag2_extremal_line_transition_census.py",
    "verify_diag2_extremal_safe_loss_edge.py",
    "verify_diag2_extremal_undominated_birth_edge.py",
    "verify_diag2_pivot_49_50_pair_saturation.py",
    "verify_diag2_robust_mutation_squares.py",
    "verify_druzkowski.py",
    "verify_sae_circuit.py",
}
CI_DELEGATED = {
    "verify_diag2_escape_set_atlas178.py",
}
fast = "--fast" in sys.argv
ci_delegated = "--ci-delegated" in sys.argv
root = os.path.dirname(os.path.abspath(__file__))

fails, ran, skipped = [], 0, 0
for dirpath, _, files in os.walk(root):
    for f in sorted(files):
        if not (f.startswith("verify_") and f.endswith(".py")):
            continue
        if fast and f in SLOW:
            skipped += 1
            print(f"SKIP  {f} (--fast)")
            continue
        if ci_delegated and f in CI_DELEGATED:
            skipped += 1
            print(f"SKIP  {f} (--ci-delegated; separate required CI job)")
            continue
        path = os.path.join(dirpath, f)
        r = subprocess.run([sys.executable, path], cwd=dirpath,
                           capture_output=True, text=True, timeout=1200)
        ran += 1
        status = "PASS" if r.returncode == 0 else "FAIL"
        print(f"{status}  {os.path.relpath(path, root)}")
        if r.returncode != 0:
            fails.append(path)
            print(r.stdout[-800:], r.stderr[-800:])

print(f"\n{ran} verifiers run, {skipped} skipped, {len(fails)} failed")
sys.exit(1 if fails else 0)
