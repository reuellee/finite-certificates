#!/usr/bin/env python3
"""Exact portable support-drop low-source and minimality census.

The dependency-free Python path exhausts the support universe.  In default
execution, when a GNU-compatible C++17 compiler is available, the original
optimized C++ census is also compiled and run as an independent implementation
cross-check.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
from itertools import combinations, permutations
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "verify_diag2_generic_birth_support_filter.cpp"

TRIPLES = tuple(
    sorted(combinations(range(8), 3), key=lambda edge: (edge[2], edge[1], edge[0]))
)
TRIPLE_INDEX = {edge: index for index, edge in enumerate(TRIPLES)}
FULL_DIRECTIONS = (1 << 56) - 1

ORDINARY_TYPES = (37, 38, 41, 42, 44, 48, 49, 50, 51)
LOCALIZATION_TYPES = (36, 39, 46, 47)

WALL_REPRESENTATIVE_TEXT = """
123/124/125/126 123/124/125/134 123/124/125/136 123/124/125/167
123/124/125/345 123/124/125/346 123/124/125/367 123/124/125/678
123/124/134/156 123/124/134/234 123/124/134/235 123/124/134/256
123/124/134/567 123/124/135/145 123/124/135/146 123/124/135/167
123/124/135/236 123/124/135/245 123/124/135/246 123/124/135/256
123/124/135/267 123/124/135/456 123/124/135/467 123/124/135/678
123/124/156/157 123/124/156/178 123/124/156/256 123/124/156/257
123/124/156/278 123/124/156/345 123/124/156/347 123/124/156/356
123/124/156/357 123/124/156/378 123/124/156/567 123/124/156/578
123/124/345/367 123/124/345/567 123/124/345/678 123/124/356/378
123/124/356/456 123/124/356/457 123/124/356/478 123/124/356/567
123/124/356/578 123/124/567/568 123/145/167/246 123/145/167/248
123/145/246/356 123/145/246/357 123/145/246/378 123/145/267/468
""".split()

LOCALIZATION_CIRCUIT_TEXT = {
    36: "123/345/367",
    39: "123/356/378",
    46: "123/145/167",
    47: "123/145/167",
}

EXPECTED_FIVE_RAW = {
    36: 8,
    37: 8,
    38: 0,
    39: 8,
    41: 8,
    42: 0,
    44: 4,
    46: 8,
    47: 8,
    48: 48,
    49: 96,
    50: 22,
    51: 76,
}
EXPECTED_FOUR_RAW = {
    37: 0,
    38: 0,
    41: 0,
    42: 0,
    44: 0,
    48: 0,
    49: 2,
    50: 0,
    51: 1,
}

EXPECTED_ORDINARY_TEXT = """
37:146/247/258/368/178
41:137/267/348/258/168
41:137/267/238/158/468
44:145/347/267/248/168
48:257/367/348/268/178
48:257/467/348/268/178
49:247/167/148/258/368
49:256/467/248/368/178
49:347/167/258/368/178
49:347/567/258/368/178
49:156/147/458/368/278
49:347/167/138/568/278
49:136/147/348/568/278
49:123/167/348/568/278
49:124/167/348/568/278
49:134/167/348/568/278
49:234/167/348/568/278
49:125/167/348/568/278
49:235/167/348/568/278
49:126/167/348/568/278
49:136/167/348/568/278
49:236/167/348/568/278
49:146/167/348/568/278
49:246/167/348/568/278
49:346/167/348/568/278
49:156/167/348/568/278
49:256/167/348/568/278
49:356/167/348/568/278
49:456/167/348/568/278
49:167/267/348/568/278
49:167/367/348/568/278
49:136/127/348/258/678
49:156/127/348/258/678
50:356/247/167/148/258
50:356/457/167/148/258
50:345/147/567/258/168
50:346/147/567/258/168
50:356/257/467/458/168
50:347/567/258/368/178
50:257/367/358/168/478
51:356/347/157/138/258
51:123/356/347/258/178
51:124/356/347/258/178
51:134/356/347/258/178
51:234/356/347/258/178
51:135/356/347/258/178
51:235/356/347/258/178
51:346/356/347/258/178
51:356/347/157/258/178
51:234/136/357/258/178
51:234/356/357/258/178
51:356/347/357/258/178
51:256/247/367/358/178
""".split()

EXPECTED_LOCALIZATION = {
    36: "156/247/258/468/178",
    39: "146/457/267/248/158",
    46: "256/347/358/468/278",
    47: "256/347/358/468/278",
}
EXPECTED_FOUR_REPRESENTATIVE = {
    49: "167/348/568/278",
    51: "356/347/258/178",
}
EXPECTED_COMPILED_STDOUT_SHA256 = (
    "faca977b2712db969807961e898f18563e2f872205c92b58dbad9acb28f2faa8"
)


class NativeToolchainUnavailable(RuntimeError):
    """The optional C++ cross-check cannot be built or launched here."""


def parse_support(text):
    support = []
    for token in text.split("/"):
        if len(token) != 3 or set(token) - set("12345678"):
            raise AssertionError(f"malformed triple in support: {token}")
        edge = tuple(sorted(int(label) - 1 for label in token))
        if len(set(edge)) != 3:
            raise AssertionError(f"repeated label in support triple: {token}")
        support.append(TRIPLE_INDEX[edge])
    if len(set(support)) != len(support):
        raise AssertionError(f"repeated triple in support: {text}")
    return tuple(sorted(support))


def support_text(support):
    return "/".join(
        "".join(str(label + 1) for label in TRIPLES[index])
        for index in support
    )


def support_mask(support):
    answer = 0
    for index in support:
        answer |= 1 << index
    return answer


def edge_tables():
    vertex_masks = []
    pair_masks = []
    coverage_masks = []
    for edge in TRIPLES:
        vertex_mask = sum(1 << vertex for vertex in edge)
        pair_mask = 0
        for left, right in combinations(edge, 2):
            pair_mask |= 1 << (8 * left + right)
        coverage_mask = 0
        for source in edge:
            for target in range(8):
                if target in edge:
                    continue
                direction = 7 * source + target - (target > source)
                coverage_mask |= 1 << direction
        vertex_masks.append(vertex_mask)
        pair_masks.append(pair_mask)
        coverage_masks.append(coverage_mask)
    return tuple(vertex_masks), tuple(pair_masks), tuple(coverage_masks)


def generic_five(support, vertex_masks, pair_masks):
    # A five-support is structurally nonminimal exactly when four triples
    # share a vertex or three triples share an unordered vertex pair.
    a, b, c, d, e = support
    va, vb, vc, vd, ve = (
        vertex_masks[a],
        vertex_masks[b],
        vertex_masks[c],
        vertex_masks[d],
        vertex_masks[e],
    )
    four_at_vertex = (
        (vb & vc & vd & ve)
        | (va & vc & vd & ve)
        | (va & vb & vd & ve)
        | (va & vb & vc & ve)
        | (va & vb & vc & vd)
    )
    if four_at_vertex:
        return False
    pa, pb, pc, pd, pe = (
        pair_masks[a],
        pair_masks[b],
        pair_masks[c],
        pair_masks[d],
        pair_masks[e],
    )
    three_at_pair = (
        (pa & pb & pc)
        | (pa & pb & pd)
        | (pa & pb & pe)
        | (pa & pc & pd)
        | (pa & pc & pe)
        | (pa & pd & pe)
        | (pb & pc & pd)
        | (pb & pc & pe)
        | (pb & pd & pe)
        | (pc & pd & pe)
    )
    return not three_at_pair


def coverage_thresholds(support, coverage_masks):
    # Bit ``d`` in ``once``/``twice`` says that at least one/two triples in
    # the support contribute to the ordered-shear source count at ``d``.
    once = 0
    twice = 0
    for index in support:
        coverage = coverage_masks[index]
        twice |= once & coverage
        once |= coverage
    return once, twice


def source_requirements(wall, coverage_masks):
    once, twice = coverage_thresholds(wall, coverage_masks)
    # A zero wall count needs two partner contributions; a one wall count
    # needs one.  Counts of at least two impose no partner condition.
    zero = FULL_DIRECTIONS ^ once
    one = once & (FULL_DIRECTIONS ^ twice)
    return zero, one


def source_hard(once, twice, requirements):
    zero, one = requirements
    return twice & zero == zero and once & one == one


def transform(support, mapping):
    return tuple(sorted(mapping[index] for index in support))


def triple_maps():
    maps = []
    for permutation in permutations(range(8)):
        maps.append(
            tuple(
                TRIPLE_INDEX[tuple(sorted(permutation[vertex] for vertex in edge))]
                for edge in TRIPLES
            )
        )
    if len(maps) != 40_320 or len(set(maps)) != 40_320:
        raise AssertionError("the S8 action on triples is not faithful")
    return tuple(maps)


def quotient(items, stabilizer):
    universe = set(items)
    remaining = set(universe)
    representatives = []
    while remaining:
        # The C++ certificate canonically orders supports by their uint64 mask.
        seed = min(remaining, key=support_mask)
        orbit = {transform(seed, mapping) for mapping in stabilizer}
        if not orbit <= universe:
            raise AssertionError("source-hard set is not wall-stabilizer invariant")
        representatives.append(min(orbit, key=support_mask))
        remaining.difference_update(orbit)
    return tuple(sorted(representatives, key=support_mask))


def expected_ordinary_representatives():
    expected = {wall_type: [] for wall_type in ORDINARY_TYPES}
    for record in EXPECTED_ORDINARY_TEXT:
        wall_type_text, support = record.split(":", 1)
        expected[int(wall_type_text)].append(parse_support(support))
    return {
        wall_type: tuple(sorted(supports, key=support_mask))
        for wall_type, supports in expected.items()
    }


def portable_audit():
    if len(TRIPLES) != 56 or len(WALL_REPRESENTATIVE_TEXT) != 52:
        raise AssertionError("wrong triple or residual-wall representative count")
    vertex_masks, pair_masks, coverage_masks = edge_tables()
    wall_representatives = tuple(
        parse_support(text) for text in WALL_REPRESENTATIVE_TEXT
    )
    active_walls = {
        wall_type: wall_representatives[wall_type]
        for wall_type in ORDINARY_TYPES
    }
    active_walls.update(
        {
            wall_type: parse_support(LOCALIZATION_CIRCUIT_TEXT[wall_type])
            for wall_type in LOCALIZATION_TYPES
        }
    )
    requirements = {
        wall_type: source_requirements(wall, coverage_masks)
        for wall_type, wall in active_walls.items()
    }
    requirement_items = tuple(requirements.items())

    hard_five = {wall_type: [] for wall_type in active_walls}
    eligible_five = 0
    five_total = 0
    for support in combinations(range(56), 5):
        five_total += 1
        if not generic_five(support, vertex_masks, pair_masks):
            continue
        eligible_five += 1
        once, twice = coverage_thresholds(support, coverage_masks)
        for wall_type, needed in requirement_items:
            if source_hard(once, twice, needed):
                hard_five[wall_type].append(support)

    hard_four = {wall_type: [] for wall_type in ORDINARY_TYPES}
    four_total = 0
    for support in combinations(range(56), 4):
        four_total += 1
        once, twice = coverage_thresholds(support, coverage_masks)
        for wall_type in ORDINARY_TYPES:
            if source_hard(once, twice, requirements[wall_type]):
                hard_four[wall_type].append(support)

    if (five_total, eligible_five, five_total - eligible_five) != (
        3_819_816,
        2_021_992,
        1_797_824,
    ):
        raise AssertionError("minimal-five eligibility census changed")
    if four_total != 367_290:
        raise AssertionError("wrong four-support count")
    actual_five_raw = {
        wall_type: len(supports) for wall_type, supports in hard_five.items()
    }
    actual_four_raw = {
        wall_type: len(supports) for wall_type, supports in hard_four.items()
    }
    if actual_five_raw != EXPECTED_FIVE_RAW:
        raise AssertionError(f"source-hard five-support counts changed: {actual_five_raw}")
    if actual_four_raw != EXPECTED_FOUR_RAW:
        raise AssertionError(f"source-hard four-support counts changed: {actual_four_raw}")

    maps = triple_maps()
    expected_ordinary = expected_ordinary_representatives()
    five_orbits = {}
    for wall_type, wall in active_walls.items():
        stabilizer = tuple(
            mapping for mapping in maps if transform(wall, mapping) == wall
        )
        if not stabilizer:
            raise AssertionError(f"wall {wall_type} has no identity stabilizer")
        five_orbits[wall_type] = quotient(hard_five[wall_type], stabilizer)
        if wall_type in ORDINARY_TYPES:
            expected = expected_ordinary[wall_type]
        else:
            expected = (parse_support(EXPECTED_LOCALIZATION[wall_type]),)
        if five_orbits[wall_type] != expected:
            actual = tuple(map(support_text, five_orbits[wall_type]))
            raise AssertionError(
                f"source-hard five-support orbits changed for type {wall_type}: {actual}"
            )

    four_orbits = {}
    for wall_type in ORDINARY_TYPES:
        wall = active_walls[wall_type]
        stabilizer = tuple(
            mapping for mapping in maps if transform(wall, mapping) == wall
        )
        four_orbits[wall_type] = quotient(hard_four[wall_type], stabilizer)
        expected_text = EXPECTED_FOUR_REPRESENTATIVE.get(wall_type)
        expected = () if expected_text is None else (parse_support(expected_text),)
        if four_orbits[wall_type] != expected:
            actual = tuple(map(support_text, four_orbits[wall_type]))
            raise AssertionError(
                f"source-hard four-support orbits changed for type {wall_type}: {actual}"
            )

    ordinary_orbits = sum(len(five_orbits[kind]) for kind in ORDINARY_TYPES)
    localization_raw = sum(actual_five_raw[kind] for kind in LOCALIZATION_TYPES)
    four_raw = sum(actual_four_raw.values())
    four_orbit_count = sum(len(four_orbits[kind]) for kind in ORDINARY_TYPES)
    if (ordinary_orbits, localization_raw, four_raw, four_orbit_count) != (
        53,
        32,
        3,
        2,
    ):
        raise AssertionError("support-drop source-hard summary changed")

    print(
        "PASS portable minimal-five eligibility",
        f"total={five_total}",
        f"eligible={eligible_five}",
        f"structurally-nonminimal={five_total - eligible_five}",
    )
    for wall_type in ORDINARY_TYPES:
        print(
            "ordinary",
            wall_type,
            f"raw={actual_five_raw[wall_type]}",
            f"orbits={len(five_orbits[wall_type])}",
        )
        for support in five_orbits[wall_type]:
            print(" ", support_text(support))
    for wall_type in LOCALIZATION_TYPES:
        print(
            "localization",
            wall_type,
            f"raw={actual_five_raw[wall_type]}",
            f"active-circuit-orbits={len(five_orbits[wall_type])}",
        )
        for support in five_orbits[wall_type]:
            print(" ", support_text(support))
    for wall_type in ORDINARY_TYPES:
        print(
            "ordinary-four-partner",
            wall_type,
            f"raw={actual_four_raw[wall_type]}",
            f"orbits={len(four_orbits[wall_type])}",
        )
        for support in four_orbits[wall_type]:
            print(" ", support_text(support))
    print(
        "SUMMARY",
        f"ordinary_orbits={ordinary_orbits}",
        f"localization_raw={localization_raw}",
        f"four_partner_raw={four_raw}",
        f"four_partner_orbits={four_orbit_count}",
    )


def parse_compiler_command(configured):
    """Parse the platform command line supplied through ``CXX``."""
    if not configured.strip():
        raise RuntimeError("CXX is set but empty")
    configured = configured.strip()
    if os.name == "nt":
        argc = ctypes.c_int()
        command_line_to_argv = ctypes.windll.shell32.CommandLineToArgvW
        command_line_to_argv.argtypes = (
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.c_int),
        )
        command_line_to_argv.restype = ctypes.POINTER(ctypes.c_wchar_p)
        argv = command_line_to_argv(configured, ctypes.byref(argc))
        if not argv:
            raise RuntimeError(f"invalid CXX command: {ctypes.WinError()}")
        try:
            return tuple(argv[index] for index in range(argc.value))
        finally:
            local_free = ctypes.windll.kernel32.LocalFree
            local_free.argtypes = (ctypes.c_void_p,)
            local_free.restype = ctypes.c_void_p
            local_free(ctypes.cast(argv, ctypes.c_void_p))
    try:
        command = shlex.split(configured, posix=True)
    except ValueError as error:
        raise RuntimeError(f"invalid CXX command: {error}") from error
    if not command:
        raise RuntimeError("CXX is set but empty")
    return tuple(command)


def compiler_candidates():
    if "CXX" in os.environ:
        command = parse_compiler_command(os.environ["CXX"])
        if shutil.which(command[0]) is None and not Path(command[0]).is_file():
            raise RuntimeError(f"CXX compiler is not executable: {command[0]}")
        return (command,), True
    candidates = []
    seen = set()
    for candidate in ("g++", "clang++"):
        resolved = shutil.which(candidate)
        if resolved is not None and resolved not in seen:
            candidates.append((resolved,))
            seen.add(resolved)
    return tuple(candidates), False


def compiled_crosscheck(compiler):
    with tempfile.TemporaryDirectory(prefix="diag2-support-drop-") as build:
        suffix = ".exe" if os.name == "nt" else ""
        executable = Path(build) / ("verify_diag2_generic_birth_support_filter" + suffix)
        command = [
            *compiler,
            "-std=c++17",
            "-O3",
            str(SOURCE),
            "-o",
            str(executable),
        ]
        try:
            compiled = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
        except OSError as error:
            raise NativeToolchainUnavailable(
                f"failed to invoke {compiler[0]}: {error}"
            ) from error
        if compiled.returncode:
            raise NativeToolchainUnavailable(
                "failed to compile support-drop C++ cross-check:\n" + compiled.stderr
            )
        try:
            completed = subprocess.run(
                [str(executable)], capture_output=True, text=True, check=False
            )
        except OSError as error:
            raise NativeToolchainUnavailable(
                f"compiled support-drop cross-check cannot be launched: {error}"
            ) from error
        if completed.returncode:
            raise RuntimeError(
                "support-drop C++ cross-check failed:\n" + completed.stderr
            )
        normalized_stdout = "\n".join(completed.stdout.splitlines()) + "\n"
        stdout_digest = hashlib.sha256(normalized_stdout.encode("utf-8")).hexdigest()
        if stdout_digest != EXPECTED_COMPILED_STDOUT_SHA256:
            raise AssertionError(
                "support-drop C++ stdout digest changed: " + stdout_digest
            )
        print("PASS independent compiled C++ cross-check", stdout_digest)


def native_failure_report(failures):
    return "\n".join(
        f"{compiler[0]}:\n{error}" for compiler, error in failures
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-compiled-crosscheck",
        action="store_true",
        help="fail unless the optional independent C++17 cross-check can run",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        compilers, explicit_compiler = compiler_candidates()
    except RuntimeError as error:
        raise SystemExit(f"ERROR: {error}") from error
    if not compilers and args.require_compiled_crosscheck:
        raise SystemExit(
            "ERROR: compiled cross-check requires CXX, g++, or clang++ with "
            "C++17 support"
        )
    portable_audit()
    if not compilers:
        print(
            "PASS exact Python census; optional compiled C++ cross-check "
            "unavailable (no supported C++17 compiler)"
        )
        return

    native_failures = []
    for compiler in compilers:
        try:
            compiled_crosscheck(compiler)
        except NativeToolchainUnavailable as error:
            native_failures.append((compiler, error))
            if explicit_compiler:
                raise SystemExit(
                    "ERROR: explicit CXX cannot run the compiled cross-check:\n"
                    f"{error}"
                ) from error
            continue
        return

    failures = native_failure_report(native_failures)
    if args.require_compiled_crosscheck:
        raise SystemExit(
            "ERROR: no auto-discovered compiler can run the compiled "
            f"cross-check:\n{failures}"
        )
    print(
        "PASS exact Python census; optional auto-discovered C++ toolchains "
        "could not build or launch the compiled cross-check"
    )


if __name__ == "__main__":
    main()
