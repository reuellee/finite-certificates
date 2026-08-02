#!/usr/bin/env python3
"""Exact, search-free gate for the proposed four-chart SEEAT bound.

The sharp parent is row 2599 of data/cat_4_8.txt.  This program:

  1. independently enumerates its 97,224 abstract uniform extensions;
  2. canonicalizes them with the independent coverage checker;
  3. optionally joins the canonical keys to an existing completed sweep
     checkpoint and certificate overlays; and
  4. counts REALIZABLE/NON_REALIZABLE statuses with labeled-extension
     multiplicity.

No LP or realization search is run.  If at most 647 extension signatures are
non-realizable, the exact universal-core bound in SEEAT.md proves that four
charts cannot cover all realizable extensions of this parent.

Typical use on the machine holding the completed sweep:

    python ai/omreal/four_chart_gate.py --state ai/omreal/sweep_state \
        --cert 'ai/omreal/sweep_state/certs/*.jsonl' \
        --cert '/path/to/final659.jsonl'

Or verify the compact standalone realization certificate shipped here:

    python ai/omreal/four_chart_gate.py \
        --realizations ai/omreal/data/seeat_parent2599_realizations.npz

Certificate overlays supersede TODO/OPEN checkpoint statuses.  Their `chi`
strings must be the canonical catalog representatives emitted by sweep49.py.
This program joins verdicts; it does not replace checkcert.py's verification
of the matrices and BFP certificates behind those verdicts.
"""

import argparse
from collections import Counter
from itertools import combinations, permutations, product
import glob
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG_48 = ROOT / "ai" / "omgamma" / "data" / "cat_4_8.txt"
EXTCOUNTS = ROOT / "ai" / "omgamma" / "data" / "extcount_4_9.jsonl"
OMMINOR = ROOT / "ai" / "omminor"

PARENT_INDEX = 2599
EXPECTED_EXTENSIONS = 97_224
EXPECTED_CHILD_CLASSES = 5_902
EXPECTED_MULTIPLICITIES = Counter({16: 5_705, 32: 182, 8: 15})
FOUR_CHART_CAPACITY = 96_576
NONREAL_REFUTATION_MAX = EXPECTED_EXTENSIONS - FOUR_CHART_CAPACITY - 1

TODO, WALK, REPAIR, NONREAL, OPEN = 0, 1, 2, 3, 4
STATUS_NAME = {
    TODO: "TODO",
    WALK: "REALIZABLE",
    REPAIR: "REALIZABLE",
    NONREAL: "NON_REALIZABLE",
    OPEN: "OPEN",
}


def colex_subsets(n, size):
    return tuple(
        sorted(
            combinations(range(1, n + 1), size),
            key=lambda subset: tuple(reversed(subset)),
        )
    )


def sort_with_sign(values):
    values = list(values)
    sign = 1
    for i in range(1, len(values)):
        j = i
        while j and values[j - 1] > values[j]:
            values[j - 1], values[j] = values[j], values[j - 1]
            sign = -sign
            j -= 1
    return tuple(values), sign


def lexicographic_signatures(parent):
    """Distinct uniform signatures [a1^e1,...,a4^e4] of a UOM(4,8)."""
    parent_bases = colex_subsets(8, 4)
    parent_index = {basis: i for i, basis in enumerate(parent_bases)}
    signatures = set()
    for sequence in permutations(range(1, 9), 4):
        for epsilons in product((1, -1), repeat=4):
            signature = 0
            for variable, triple in enumerate(colex_subsets(8, 3)):
                for element, epsilon in zip(sequence, epsilons):
                    if element in triple:
                        continue
                    basis, alternating_sign = sort_with_sign(triple + (element,))
                    parent_sign = 1 if parent[parent_index[basis]] == "+" else -1
                    if epsilon * alternating_sign * parent_sign > 0:
                        signature |= 1 << variable
                    break
            signatures.add(signature)
    return signatures


def det3(a, b, c, columns):
    i, j, k = columns
    return (
        a[i] * (b[j] * c[k] - b[k] * c[j])
        - a[j] * (b[i] * c[k] - b[k] * c[i])
        + a[k] * (b[i] * c[j] - b[j] * c[i])
    )


def det4(a, b, c, d):
    return (
        a[0] * det3(b, c, d, (1, 2, 3))
        - a[1] * det3(b, c, d, (0, 2, 3))
        + a[2] * det3(b, c, d, (0, 1, 3))
        - a[3] * det3(b, c, d, (0, 1, 2))
    )


def exact_matrix_key(matrix):
    """Exact manifest key of a 4x9 integer matrix, or fail on a zero bracket."""
    if matrix.shape != (4, 9):
        raise ValueError(f"realization matrix has shape {matrix.shape}, not (4, 9)")
    columns = [tuple(int(matrix[row, col]) for row in range(4)) for col in range(9)]
    key = 0
    for basis in colex_subsets(9, 4):
        determinant = det4(*(columns[element - 1] for element in basis))
        if determinant == 0:
            raise ValueError(f"zero bracket at basis {basis}")
        key = (key << 1) | int(determinant > 0)
    return key >> 64, key & ((1 << 64) - 1)


def compile_extension_system(parent_bits):
    """Compile GP constraints involving new element 9.

    This is deliberately self-contained: it does not import the catalog
    generator's extension enumerator before invoking the independent checker.
    Bit 1 means a positive chirotope value; parity 0 means a positive signed
    GP term.
    """
    m, r, new_element = 8, 4, 9
    new_bases = colex_subsets(m, r - 1)
    new_index = {basis: i for i, basis in enumerate(new_bases)}
    parent_index = {basis: i for i, basis in enumerate(colex_subsets(m, r))}
    by_last = [[] for _ in new_bases]

    for lam in combinations(range(1, new_element + 1), r - 2):
        rest = [x for x in range(1, new_element + 1) if x not in lam]
        for a, b, c, d in combinations(rest, 4):
            if new_element not in lam and new_element not in (a, b, c, d):
                continue
            terms = []
            for pairs, explicit_minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                variables = []
                constant = explicit_minus
                for x, y in pairs:
                    basis, alternating_sign = sort_with_sign(lam + (x, y))
                    constant ^= alternating_sign < 0
                    if new_element in basis:
                        triple = tuple(z for z in basis if z != new_element)
                        variables.append(new_index[triple])
                    else:
                        constant ^= int(parent_bits[parent_index[basis]])
                terms.append((tuple(variables), int(constant)))
            last = max(variable for variables, _ in terms for variable in variables)
            by_last[last].append(tuple(terms))
    return tuple(tuple(rows) for rows in by_last)


def enumerate_extensions(parent):
    """Return every valid 56-bit extension signature by exact backtracking."""
    parent_bits = np.fromiter((sign == "+" for sign in parent), dtype=np.uint8)
    by_last = compile_extension_system(parent_bits)
    nvars = len(by_last)
    values = [0] * nvars
    next_value = [0] * nvars
    signatures = []
    depth = 0

    while True:
        if next_value[depth] > 1:
            next_value[depth] = 0
            depth -= 1
            if depth < 0:
                break
            next_value[depth] += 1
            continue

        values[depth] = next_value[depth]
        valid = True
        for relation in by_last[depth]:
            parities = []
            for variables, constant in relation:
                parity = constant
                for variable in variables:
                    parity ^= values[variable]
                parities.append(parity)
            if parities[0] == parities[1] == parities[2]:
                valid = False
                break

        if not valid:
            next_value[depth] += 1
        elif depth == nvars - 1:
            signature = 0
            for variable, value in enumerate(values):
                signature |= value << variable
            signatures.append(signature)
            next_value[depth] += 1
        else:
            depth += 1
            next_value[depth] = 0

    return parent_bits, signatures


def extension_bit_matrix(parent_bits, signatures):
    signatures = np.asarray(signatures, dtype=np.uint64)
    matrix = np.empty((len(signatures), 126), dtype=np.uint8)
    matrix[:, :70] = parent_bits
    shifts = np.arange(56, dtype=np.uint64)
    matrix[:, 70:] = ((signatures[:, None] >> shifts) & 1).astype(np.uint8)
    return matrix


def direct_catalog_key(chi):
    """Canonical sign string -> manifest's split 126-bit key."""
    if len(chi) != 126 or set(chi) - {"+", "-"}:
        raise ValueError("certificate chi is not a 126-sign UOM(4,9) string")
    key = int("".join("1" if sign == "+" else "0" for sign in chi), 2)
    return key >> 64, key & ((1 << 64) - 1)


def checkpoint_statuses(state, wanted, chunk=1 << 20):
    hi_path = state / "hi.npy"
    lo_path = state / "lo.npy"
    status_path = state / "st.dat"
    for path in (hi_path, lo_path, status_path):
        if not path.exists():
            raise SystemExit(f"missing sweep checkpoint file: {path}")

    hi = np.load(hi_path, mmap_mode="r")
    lo = np.load(lo_path, mmap_mode="r")
    if len(hi) != len(lo):
        raise SystemExit("hi.npy and lo.npy have different lengths")
    statuses = np.memmap(status_path, dtype=np.uint8, mode="r", shape=(len(hi),))

    wanted_hi = np.asarray(sorted({key[0] for key in wanted}), dtype=np.uint64)
    found = {}
    for start in range(0, len(hi), chunk):
        stop = min(start + chunk, len(hi))
        high_chunk = np.asarray(hi[start:stop])
        candidates = np.flatnonzero(np.isin(high_chunk, wanted_hi))
        for offset in candidates:
            key = (int(high_chunk[offset]), int(lo[start + offset]))
            if key in wanted:
                if key in found:
                    raise SystemExit(f"duplicate catalog key in checkpoint: {key}")
                found[key] = int(statuses[start + offset])
    missing = set(wanted) - set(found)
    if missing:
        raise SystemExit(f"{len(missing)} target classes are absent from the checkpoint")
    return found


def overlay_certificates(statuses, patterns, wanted):
    files = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if not matches:
            raise SystemExit(f"certificate pattern matched no files: {pattern}")
        files.extend(matches)

    used = 0
    for filename in files:
        with open(filename, encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                record = json.loads(line)
                key = direct_catalog_key(record["chi"])
                if key not in wanted:
                    continue
                verdict = record.get("verdict")
                if verdict == "REALIZABLE":
                    new_status = REPAIR
                elif verdict == "NON_REALIZABLE":
                    new_status = NONREAL
                elif verdict in ("RESIDUE", "OPEN"):
                    new_status = OPEN
                else:
                    raise SystemExit(
                        f"{filename}:{line_number}: unknown verdict {verdict!r}"
                    )
                old_status = statuses.get(key, TODO)
                old_final = STATUS_NAME.get(old_status) in {
                    "REALIZABLE",
                    "NON_REALIZABLE",
                }
                new_final = STATUS_NAME[new_status] in {
                    "REALIZABLE",
                    "NON_REALIZABLE",
                }
                contradicts = (
                    old_final
                    and new_final
                    and STATUS_NAME[old_status] != STATUS_NAME[new_status]
                )
                if contradicts:
                    raise SystemExit(
                        f"{filename}:{line_number}: verdict contradicts an earlier "
                        f"record for key {key}"
                    )
                if new_final or not old_final:
                    statuses[key] = new_status
                used += 1
    return len(files), used


def verify_realization_certificate(path, key_multiplicity, progress=False):
    """Verify one exact matrix for every target child class."""
    artifact = np.load(path, allow_pickle=False)
    required = {
        "format",
        "parent_index",
        "key_hi",
        "key_lo",
        "multiplicity",
        "matrix",
    }
    if set(artifact.files) != required:
        raise SystemExit(
            f"{path}: fields {sorted(artifact.files)} != {sorted(required)}"
        )
    if str(artifact["format"].item()) != "seeat-parent2599-realizations-v1":
        raise SystemExit(f"{path}: unknown certificate format")
    if int(artifact["parent_index"].item()) != PARENT_INDEX:
        raise SystemExit(f"{path}: wrong parent index")

    hi = artifact["key_hi"]
    lo = artifact["key_lo"]
    multiplicity = artifact["multiplicity"]
    matrices = artifact["matrix"]
    if hi.shape != (EXPECTED_CHILD_CLASSES,) or lo.shape != hi.shape:
        raise SystemExit(f"{path}: wrong key-array shape")
    if multiplicity.shape != hi.shape:
        raise SystemExit(f"{path}: wrong multiplicity-array shape")
    if matrices.shape != (EXPECTED_CHILD_CLASSES, 4, 9):
        raise SystemExit(f"{path}: wrong matrix-array shape")
    if not np.issubdtype(matrices.dtype, np.integer):
        raise SystemExit(f"{path}: matrices are not integers")

    expected = sorted(key_multiplicity)
    supplied = [(int(h), int(l)) for h, l in zip(hi, lo)]
    if supplied != expected:
        raise SystemExit(f"{path}: child keys do not exactly match the gate")
    expected_multiplicity = np.asarray(
        [key_multiplicity[key] for key in expected], dtype=np.int64
    )
    if not np.array_equal(multiplicity.astype(np.int64), expected_multiplicity):
        raise SystemExit(f"{path}: extension multiplicities do not match the gate")

    for i, (key, matrix) in enumerate(zip(supplied, matrices), 1):
        try:
            realized_key = exact_matrix_key(matrix)
        except ValueError as error:
            raise SystemExit(f"{path}: matrix {i - 1}: {error}") from error
        if realized_key != key:
            raise SystemExit(
                f"{path}: matrix {i - 1} realizes {realized_key}, expected {key}"
            )
        if progress and i % 1_000 == 0:
            print(f"  exact matrices {i}/{EXPECTED_CHILD_CLASSES}", flush=True)
    return {key: REPAIR for key in supplied}


def report_gate(key_multiplicity, statuses):
    signing_counts = Counter()
    class_counts = Counter()
    for key, multiplicity in key_multiplicity.items():
        status = statuses.get(key, TODO)
        name = STATUS_NAME.get(status, f"UNKNOWN_STATUS_{status}")
        signing_counts[name] += multiplicity
        class_counts[name] += 1

    print("status                 classes   extension_signatures")
    for name in (
        "REALIZABLE",
        "NON_REALIZABLE",
        "OPEN",
        "TODO",
    ):
        print(f"{name:22s} {class_counts[name]:8d} {signing_counts[name]:22d}")
    standard = {"REALIZABLE", "NON_REALIZABLE", "OPEN", "TODO"}
    extras = sorted(set(signing_counts) - standard)
    for name in extras:
        print(f"{name:22s} {class_counts[name]:8d} {signing_counts[name]:22d}")

    unresolved = (
        EXPECTED_EXTENSIONS
        - signing_counts["REALIZABLE"]
        - signing_counts["NON_REALIZABLE"]
    )
    if unresolved:
        print(f"GATE UNRESOLVED: {unresolved} extension signatures lack a final verdict")
        return 2

    nonreal = signing_counts["NON_REALIZABLE"]
    realizable = signing_counts["REALIZABLE"]
    if nonreal <= NONREAL_REFUTATION_MAX:
        assert realizable >= FOUR_CHART_CAPACITY + 1
        print(
            "FOUR-CHART REFUTED: "
            f"{realizable} realizable signatures > {FOUR_CHART_CAPACITY} capacity "
            f"({nonreal} nonreal <= {NONREAL_REFUTATION_MAX})."
        )
        return 0

    print(
        "FOUR-CHART NOT PROVED: the counting obstruction does not fire "
        f"({nonreal} nonreal >= 648).  An explicit four-chart cover and its "
        "coverage certificate are still required."
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state",
        type=Path,
        help="completed sweep_state directory containing hi.npy, lo.npy, st.dat",
    )
    parser.add_argument(
        "--cert",
        action="append",
        default=[],
        help="JSONL certificate path or glob; may be repeated",
    )
    parser.add_argument(
        "--realizations",
        type=Path,
        help="compact exact-matrix certificate for all target child classes",
    )
    parser.add_argument("--batch", type=int, default=500)
    args = parser.parse_args()

    parents = [line.strip() for line in CATALOG_48.open() if line.strip()]
    parent = parents[PARENT_INDEX]
    counts = {
        record["i"]: record
        for record in (json.loads(line) for line in EXTCOUNTS.open() if line.strip())
    }
    if counts[PARENT_INDEX]["E"] != EXPECTED_EXTENSIONS:
        raise SystemExit("tracked extension count for parent 2599 changed")
    lex_core = lexicographic_signatures(parent)
    if len(lex_core) != 2_624:
        raise SystemExit("lexicographic universal core did not reproduce 2624")
    four_capacity = 4 * 26_112 - 3 * len(lex_core)
    if four_capacity != FOUR_CHART_CAPACITY:
        raise SystemExit("four-chart capacity did not reproduce 96576")
    print("PASS exact universal core: 2624; four-chart capacity: 96576")

    parent_bits, signatures = enumerate_extensions(parent)
    if len(signatures) != EXPECTED_EXTENSIONS or len(set(signatures)) != len(signatures):
        raise SystemExit("independent extension enumeration did not reproduce E=97224")
    print(f"PASS independent extension enumeration: {len(signatures)} signatures")

    # Import only the checker side after enumeration.  coverage_checker.py's
    # independence gate rejects a process that imported the generator modules.
    sys.path.insert(0, str(OMMINOR))
    import minorlib as ml

    extension_bits = extension_bit_matrix(parent_bits, signatures)
    hi, lo, _nargmax, valid = ml.canon_keys(9, 4, extension_bits, batch=args.batch)
    if not valid.all():
        raise SystemExit("coverage checker rejected an enumerated extension")
    key_multiplicity = Counter((int(h), int(l)) for h, l in zip(hi, lo))
    if sum(key_multiplicity.values()) != EXPECTED_EXTENSIONS:
        raise SystemExit("canonical multiplicities do not sum to E=97224")
    if len(key_multiplicity) != EXPECTED_CHILD_CLASSES:
        raise SystemExit("independent canonicalization did not reproduce 5902 classes")
    multiplicity_histogram = Counter(key_multiplicity.values())
    if multiplicity_histogram != EXPECTED_MULTIPLICITIES:
        raise SystemExit("child-class multiplicity histogram changed")
    print(
        "PASS independent canonicalization: "
        f"{len(key_multiplicity)} child classes, multiplicity sum 97224"
    )
    print("PASS exact multiplicities: 15x8 + 5705x16 + 182x32 = 97224")
    print(
        "EXACT FOUR-CHART GATE: <=647 nonreal signatures refutes four; "
        ">=648 only avoids this counting obstruction"
    )

    statuses = {}
    if args.state is not None:
        statuses = checkpoint_statuses(args.state, key_multiplicity)
        print(f"PASS checkpoint join: {len(statuses)} target child classes located")
    if args.realizations is not None:
        realized = verify_realization_certificate(
            args.realizations, key_multiplicity, progress=True
        )
        for key, status in realized.items():
            old = statuses.get(key, TODO)
            if old == NONREAL:
                raise SystemExit(
                    f"exact matrix contradicts NON_REALIZABLE status for key {key}"
                )
            statuses[key] = status
        print(
            "PASS standalone realization certificate: "
            f"{len(realized)} exact child matrices"
        )
    if args.cert:
        file_count, used = overlay_certificates(statuses, args.cert, key_multiplicity)
        print(f"PASS certificate overlay: {used} target records from {file_count} files")

    if args.state is None and args.realizations is None and not args.cert:
        print(
            "No verdict source supplied.  Re-run with --state on the completed "
            "sweep checkpoint (and --cert for any final overlays)."
        )
        return 2
    return report_gate(key_multiplicity, statuses)


if __name__ == "__main__":
    raise SystemExit(main())
