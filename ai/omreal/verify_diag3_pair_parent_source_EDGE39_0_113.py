#!/usr/bin/env python3
"""Independent exact label/profile referee for the frozen edge-39 candidate.

No candidate producer or verifier module is imported or executed.  The script
implements the extension constraints, exact central-arrangement tope census,
simple mutations, compound chamber re-enumeration, packed-profile parser, and
regular-path/collar interface checks directly from pinned raw inputs.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import gzip
import json
import os
import struct

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "ai/omreal/data"
TRANSITION_PATH = "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json"
LABELS_PATH = "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113.json"
PROFILES_PATH = "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113_PROFILES.bin.gz"
POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
PARENT_CATALOG = ROOT / "ai/omgamma/data/cat_4_8.txt"
COLLAR = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
SOURCE = 0
TARGET = 113
EVENTS = 5327
CHAMBERS = 5328
SIGNATURES = 97224
TOPES = 26112
PROFILE_BYTES = 666
PROFILE_MAGIC = b"D3E39P1\0"
EXPECTED_TRANSITION_SHA = "cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7"
EXPECTED_LABEL_SHA = "dc80acaf2f711ee5e0e053e856e4abf858adf90483ba0e5ced13018bdb909170"
EXPECTED_PROFILE_SHA = "77b042d72e4c28dc5e60145624adfd27b080aaec8aa757cdf10c0d7c5513e6b6"
# The public 2^-22 event boxes are already strictly separated except at two
# adjacent pairs.  These two independently audited 2^-48 refinements retain
# only the strict post-event gaps needed for exact chamber sampling; no
# discovery-side roadmap or checker is imported or executed.
STRICT_POST_EVENT_GAPS = {
    4427: (
        Fraction("250831842129911/281474976710656"),
        Fraction("15676990165095/17592186044416"),
    ),
    4558: (
        Fraction("63867524441991/70368744177664"),
        Fraction("255470191662431/281474976710656"),
    ),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def artifact_bytes(path):
    return (ROOT / path).read_bytes()


def digest_file(path):
    h = sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def colex(n, size):
    return tuple(sorted(combinations(range(n), size), key=lambda x: tuple(reversed(x))))


TRIPLES = colex(8, 3)
BASES = colex(8, 4)


def determinant(matrix):
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    return sum(
        (-1 if j & 1 else 1)
        * matrix[0][j]
        * determinant(tuple(row[:j] + row[j + 1 :] for row in matrix[1:]))
        for j in range(n)
    )


def minor(matrix, columns):
    return determinant(tuple(tuple(int(matrix[r][c]) for c in columns) for r in range(4)))


def normalized_values(matrix):
    basis = (0, 1, 2, 3)
    denominators = tuple(
        minor(matrix, basis[:r] + (4,) + basis[r + 1 :]) for r in range(4)
    )
    if any(not value for value in denominators):
        raise AssertionError("nonuniform normalization frame")
    values = []
    for column in (5, 6, 7):
        raw = tuple(
            Fraction(minor(matrix, basis[:r] + (column,) + basis[r + 1 :]), denominators[r])
            for r in range(4)
        )
        if not raw[0]:
            raise AssertionError("zero projective gauge")
        scaled = tuple(value / raw[0] for value in raw)
        if scaled[0] != 1 or any(value <= 0 for value in scaled):
            raise AssertionError("normalized column left positive chart")
        values.extend(scaled[1:])
    return tuple(values)


def integer_parent(values):
    columns = []
    for c in range(4):
        columns.append(tuple(1 if r == c else 0 for r in range(4)))
    columns.append((1, 1, 1, 1))
    for block in range(3):
        column = (Fraction(1),) + tuple(values[3 * block : 3 * block + 3])
        scale = 1
        for value in column:
            scale = lcm(scale, value.denominator)
        columns.append(tuple(int(scale * value) for value in column))
    return tuple(tuple(columns[c][r] for c in range(8)) for r in range(4))


def primitive_vector(vector):
    vector = tuple(map(int, vector))
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    divisor = max(divisor, 1)
    return tuple(value // divisor for value in vector)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def derived_normals(parent):
    answer = []
    for triple in TRIPLES:
        columns = tuple(tuple(int(parent[r][c]) for c in triple) for r in range(4))
        normal = []
        for coordinate in range(4):
            submatrix = tuple(row for r, row in enumerate(columns) if r != coordinate)
            normal.append((-1) ** (coordinate + 3) * determinant(submatrix))
        row = primitive_vector(normal)
        if not any(row):
            raise AssertionError("uniform parent produced zero normal")
        answer.append(row)
    return tuple(answer)


def restrict_rows(rows, normal):
    pivot = next(i for i, value in enumerate(normal) if value)
    free = tuple(i for i in range(len(normal)) if i != pivot)
    p = normal[pivot]
    restricted = tuple(
        primitive_vector(p * row[i] - row[pivot] * normal[i] for i in free)
        for row in rows
    )
    return restricted, pivot, free


def lift(witness, normal, pivot, free):
    vector = [0] * len(normal)
    p = normal[pivot]
    for i, value in zip(free, witness):
        vector[i] = p * value
    vector[pivot] = -sum(normal[i] * value for i, value in zip(free, witness))
    answer = primitive_vector(vector)
    if dot(normal, answer):
        raise AssertionError("restriction lift")
    return answer


def enumerate_regions(rows, dimension=None):
    rows = tuple(primitive_vector(row) for row in rows)
    if dimension is None:
        dimension = len(rows[0])
    if any(not any(row) for row in rows):
        return {}
    if not rows:
        return {0: (1,) + (0,) * (dimension - 1)}
    if dimension == 1:
        positive = sum((row[0] > 0) << i for i, row in enumerate(rows))
        return {positive: (1,), ((1 << len(rows)) - 1) ^ positive: (-1,)}

    regions = {0: (1,) + (0,) * (dimension - 1)}
    for index, normal in enumerate(rows):
        restricted, pivot, free = restrict_rows(rows[:index], normal)
        boundary = {
            signs: lift(witness, normal, pivot, free)
            for signs, witness in enumerate_regions(restricted, dimension - 1).items()
        }
        new = {}
        for signs, witness in regions.items():
            if signs in boundary:
                continue
            value = dot(normal, witness)
            if not value:
                raise AssertionError("old chamber witness on new wall")
            new[signs | ((value > 0) << index)] = witness
        for signs, wall in boundary.items():
            k = 1
            for old in rows[:index]:
                margin, slope = dot(old, wall), dot(old, normal)
                if not margin:
                    raise AssertionError("nonstrict boundary witness")
                if slope:
                    k = max(k, abs(slope) // abs(margin) + 1)
            plus = primitive_vector(k * x + y for x, y in zip(wall, normal))
            minus = primitive_vector(k * x - y for x, y in zip(wall, normal))
            if dot(normal, plus) <= 0 or dot(normal, minus) >= 0:
                raise AssertionError("wall perturbation orientation")
            new[signs | (1 << index)] = plus
            new[signs] = minus
        regions = new
    return regions


def parent_signs(parent):
    answer = []
    for basis in BASES:
        value = minor(parent, basis)
        if not value:
            raise AssertionError("nonuniform parent basis")
        answer.append(value > 0)
    return tuple(answer)


def solve_reorientation(normalized, raw):
    pivots = {}
    for basis, left, right in zip(BASES, parent_signs(normalized), parent_signs(raw), strict=True):
        word = 1
        for i in basis:
            word |= 1 << (i + 1)
        value = int(left != right)
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (word, value)
                break
            previous, bit = pivots[pivot]
            word ^= previous
            value ^= bit
        else:
            if value:
                raise AssertionError("reorientation equations inconsistent")
    if len(pivots) != 8:
        raise AssertionError(("reorientation rank", len(pivots)))
    solution = 0
    for pivot in sorted(pivots):
        word, value = pivots[pivot]
        bit = value ^ ((word & solution).bit_count() & 1)
        solution |= bit << pivot
    mask = 0
    for index, triple in enumerate(TRIPLES):
        bit = solution & 1
        for element in triple:
            bit ^= (solution >> (element + 1)) & 1
        mask |= bit << index
    return mask


def sorted_with_parity(values):
    values = tuple(values)
    inversions = sum(values[i] > values[j] for i in range(len(values)) for j in range(i + 1, len(values)))
    return tuple(sorted(values)), -1 if inversions & 1 else 1


def extension_universe(parent_word):
    parent_bits = tuple(character == "+" for character in parent_word)
    parent_index = {basis: i for i, basis in enumerate(colex(8, 4))}
    new_bases = colex(8, 3)
    new_index = {basis: i for i, basis in enumerate(new_bases)}
    constraints = [[] for _ in new_bases]
    for lam in combinations(range(1, 10), 2):
        remaining = [x for x in range(1, 10) if x not in lam]
        for a, b, c, d in combinations(remaining, 4):
            if 9 not in lam and 9 not in (a, b, c, d):
                continue
            terms = []
            for pairs, explicit_minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                variables = []
                parity = explicit_minus
                for x, y in pairs:
                    basis, alternating = sorted_with_parity(lam + (x, y))
                    parity ^= alternating < 0
                    zero_basis = tuple(value - 1 for value in basis)
                    if 8 in zero_basis:
                        triple = tuple(value for value in zero_basis if value != 8)
                        variables.append(new_index[triple])
                    else:
                        parity ^= parent_bits[parent_index[zero_basis]]
                terms.append((tuple(variables), int(parity)))
            last = max(variable for variables, _ in terms for variable in variables)
            constraints[last].append(tuple(terms))

    values = [0] * 56
    next_value = [0] * 56
    answer = []
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
        for relation in constraints[depth]:
            parities = []
            for variables, constant in relation:
                value = constant
                for variable in variables:
                    value ^= values[variable]
                parities.append(value)
            if parities[0] == parities[1] == parities[2]:
                valid = False
                break
        if not valid:
            next_value[depth] += 1
        elif depth == 55:
            signature = sum(value << i for i, value in enumerate(values))
            answer.append(signature)
            next_value[depth] += 1
        else:
            depth += 1
            next_value[depth] = 0
    result = tuple(sorted(answer))
    if len(result) != len(set(result)) or len(result) != SIGNATURES:
        raise AssertionError(("extension universe census", len(result)))
    return result


def label_digest(labels):
    digest = sha256(b"diag3-row2599-edge39-label-set-v1\0")
    for signature in sorted(labels):
        digest.update(int(signature).to_bytes(7, "little"))
    return digest.hexdigest()


def simple_mutation(labels, basis):
    basis = tuple(map(int, basis))
    basis_set = set(basis)
    mask = sum(1 << index for index in basis)
    preliminary = []
    for signature in labels:
        if signature ^ mask in labels:
            continue
        if all(signature ^ (1 << index) in labels for index in basis):
            preliminary.append(signature)
    lost = []
    for signature in preliminary:
        neighbors = {index for index in range(56) if signature ^ (1 << index) in labels}
        if neighbors == basis_set:
            lost.append(signature)
    if len(lost) != 2 or lost[0] ^ lost[1] != (1 << 56) - 1:
        raise AssertionError(("nonsimplicial event", basis, len(preliminary), len(lost)))
    gained = {signature ^ mask for signature in lost}
    if gained & labels:
        raise AssertionError("simple mutation gains existing tope")
    return (labels - set(lost)) | gained, len(preliminary)


WORK_X0 = WORK_DX = None
WORK_MASK = None


def worker_init(x0, dx, mask):
    global WORK_X0, WORK_DX, WORK_MASK
    WORK_X0, WORK_DX, WORK_MASK = x0, dx, mask


def compound_state(task):
    event_index, parameter = task
    values = tuple(a + parameter * d for a, d in zip(WORK_X0, WORK_DX))
    parent = integer_parent(values)
    regions = enumerate_regions(derived_normals(parent))
    if len(regions) != TOPES:
        raise AssertionError(("compound exact tope census", event_index, len(regions)))
    labels = tuple(sorted(signature ^ WORK_MASK for signature in regions))
    return event_index, labels


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    transition_raw = artifact_bytes(TRANSITION_PATH)
    labels_raw = artifact_bytes(LABELS_PATH)
    profiles_gz = artifact_bytes(PROFILES_PATH)
    require(sha256(transition_raw).hexdigest() == EXPECTED_TRANSITION_SHA, "transition digest")
    require(sha256(labels_raw).hexdigest() == EXPECTED_LABEL_SHA, "label digest")
    require(sha256(profiles_gz).hexdigest() == EXPECTED_PROFILE_SHA, "profile digest")
    transition = json.loads(transition_raw)
    certificate = json.loads(labels_raw)
    events = transition["residual_roadmap"]["events"]
    records = certificate["continuation"]["event_records"]
    require(len(events) == len(records) == EVENTS, "event alignment census")
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    require(matrices.shape == (178, 4, 8), "point bank")
    x0 = normalized_values(matrices[SOURCE])
    x1 = normalized_values(matrices[TARGET])
    dx = tuple(b - a for a, b in zip(x0, x1))
    normalized_zero = integer_parent(x0)
    raw_zero = tuple(tuple(map(int, row)) for row in matrices[SOURCE])
    mask = solve_reorientation(normalized_zero, raw_zero)
    require(mask == 66239625586952485, "independent reorientation mask")

    parent_word = PARENT_CATALOG.read_text(encoding="ascii").splitlines()[2599].strip()
    require(len(parent_word) == 70 and set(parent_word) <= {"+", "-"}, "parent catalog word")
    universe = extension_universe(parent_word)
    universe_index = {signature: index for index, signature in enumerate(universe)}
    universe_digest = sha256(b"edge39-referee-extension-universe-v1\0")
    for signature in universe:
        universe_digest.update(signature.to_bytes(7, "little"))

    normalized_labels = set(enumerate_regions(derived_normals(normalized_zero)))
    labels = {signature ^ mask for signature in normalized_labels}
    raw_source = set(enumerate_regions(derived_normals(raw_zero)))
    require(labels == raw_source and len(labels) == TOPES, "source raw/normalized labels")

    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.int64)
        occurrence_fourset = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
    event_factor_ids = {int(event["members"][0]["factor_id"]) for event in events}
    occurrences = {
        factor_id: tuple(
            tuple(map(int, row))
            for row in occurrence_fourset[np.flatnonzero(occurrence_factor == factor_id)]
        )
        for factor_id in event_factor_ids
    }
    for event in events:
        member = event["members"][0]
        require(len(occurrences[int(member["factor_id"])]) == int(member["occurrence_multiplicity"]), "raw occurrence grouping")

    compound_tasks = []
    for index, event in enumerate(events):
        if int(event["members"][0]["occurrence_multiplicity"]) == 1:
            continue
        right = Fraction(event["isolating_interval"][1])
        next_left = (
            Fraction(events[index + 1]["isolating_interval"][0])
            if index + 1 < len(events)
            else Fraction(1)
        )
        if right >= next_left:
            require(index in STRICT_POST_EVENT_GAPS, ("unrefined touching event boxes", index))
            refined_right, refined_next_left = STRICT_POST_EVENT_GAPS[index]
            require(
                Fraction(event["isolating_interval"][0]) < refined_right <= right,
                ("refined current-root bound", index),
            )
            require(
                next_left <= refined_next_left < Fraction(events[index + 1]["isolating_interval"][1]),
                ("refined next-root bound", index),
            )
            right, next_left = refined_right, refined_next_left
        require(right < next_left, "post-event sample chamber")
        compound_tasks.append((index, (right + next_left) / 2))
    require(set(STRICT_POST_EVENT_GAPS) == {4427, 4558}, "strict-gap refinement census")
    require(len(compound_tasks) == 293, "compound task census")
    workers = max(
        1,
        min(6, int(os.environ.get("DIAG3_EDGE39_REFEREE_WORKERS", "4"))),
    )
    print("PRECOMPUTE", len(compound_tasks), "compound states with", workers, "workers", flush=True)
    if workers == 1:
        compound_rows = map(compound_state, compound_tasks)
        worker_init(x0, dx, mask)
    else:
        executor = ProcessPoolExecutor(max_workers=workers, initializer=worker_init, initargs=(x0, dx, mask))
        compound_rows = executor.map(compound_state, compound_tasks, chunksize=1)
    compound = dict(compound_rows)
    if workers != 1:
        executor.shutdown()

    profiles = np.zeros((SIGNATURES, PROFILE_BYTES), dtype=np.uint8)
    chamber_digests = []

    def record_chamber(index, current):
        require(len(current) == TOPES, ("chamber tope census", index, len(current)))
        try:
            indices = np.fromiter((universe_index[value] for value in current), dtype=np.int64, count=TOPES)
        except KeyError as error:
            raise AssertionError(("chamber left extension universe", index)) from error
        profiles[indices, index // 8] |= np.uint8(1 << (index & 7))
        chamber_digests.append(label_digest(current))

    record_chamber(0, labels)
    simple_candidates = Counter()
    compound_deltas = Counter()
    computed_event_rows = []
    for index, (event, declared) in enumerate(zip(events, records, strict=True)):
        member = event["members"][0]
        factor_id = int(member["factor_id"])
        require(declared["event_index"] == index and declared["factor_ids"] == [factor_id], ("declared event identity", index))
        before = labels
        if int(member["occurrence_multiplicity"]) == 1:
            labels, candidates = simple_mutation(labels, occurrences[factor_id][0])
            simple_candidates[candidates] += 1
            method = "simplicial_basis_mutation"
        else:
            labels = set(compound[index])
            method = "exact_post_event_tope_reenumeration"
        lost, gained = before - labels, labels - before
        require(len(lost) == len(gained), ("unbalanced event", index))
        if method == "simplicial_basis_mutation":
            require((len(lost), len(gained)) == (2, 2), ("simple delta", index))
        else:
            compound_deltas[(int(member["occurrence_multiplicity"]), len(lost), len(gained))] += 1
        record_chamber(index + 1, labels)
        row = {
            "event_index": index,
            "factor_ids": [factor_id],
            "method": method,
            "lost_labels": len(lost),
            "gained_labels": len(gained),
            "post_chamber_labels_sha256": chamber_digests[-1],
        }
        require(declared == row, ("declared label event", index))
        computed_event_rows.append(row)
        if (index + 1) % 500 == 0:
            print("CONTINUED", index + 1, "/", EVENTS, flush=True)

    raw_target = set(enumerate_regions(derived_normals(tuple(tuple(map(int, row)) for row in matrices[TARGET]))))
    require(labels == raw_target, "terminal raw chart-113 labels")
    require(records[5236]["factor_ids"] == [19069] and records[5236]["method"] == "simplicial_basis_mutation", "factor19069 label event")

    continuation = certificate["continuation"]
    require(continuation["extension_signature_universe"] == SIGNATURES, "declared universe")
    require(continuation["labels_per_generic_chamber"] == TOPES, "declared tope census")
    require(continuation["ordered_event_groups"] == EVENTS, "declared event census")
    require(continuation["simple_mutation_events"] == sum(simple_candidates.values()) == 5034, "simple continuation census")
    require(continuation["compound_or_tangential_reenumeration_events"] == sum(compound_deltas.values()) == 293, "compound continuation census")
    require(continuation["simple_preliminary_candidate_census"] == {str(k): v for k, v in sorted(simple_candidates.items())}, "simple candidate census")
    declared_compound = {
        f"occurrence_{m}:algebraic_1:lost_{lost}:gained_{gained}": count
        for (m, lost, gained), count in sorted(compound_deltas.items())
    }
    require(continuation["compound_delta_census"] == declared_compound, "compound delta census")
    require(continuation["chart_113_raw_label_state_reconstructed"] is True, "terminal declaration")

    chamber_digest = sha256(b"diag3-row2599-edge39-chamber-label-digests-v1\0")
    for value in chamber_digests:
        chamber_digest.update(bytes.fromhex(value))
    event_digest = sha256(b"diag3-row2599-edge39-label-events-v1\0")
    for row in computed_event_rows:
        event_digest.update(row["event_index"].to_bytes(4, "little"))
        for factor_id in row["factor_ids"]:
            event_digest.update(factor_id.to_bytes(4, "little"))
        event_digest.update(row["lost_labels"].to_bytes(4, "little"))
        event_digest.update(bytes.fromhex(row["post_chamber_labels_sha256"]))
    require(continuation["chamber_label_digests_sha256"] == chamber_digest.hexdigest(), "chamber digest")
    require(continuation["event_label_semantic_sha256"] == event_digest.hexdigest(), "event digest")

    require(profiles_gz[4:8] == b"\0\0\0\0", "deterministic gzip mtime")
    raw = gzip.decompress(profiles_gz)
    require(raw[:8] == PROFILE_MAGIC, "profile magic")
    signature_count, chamber_count, row_width = struct.unpack_from("<III", raw, 8)
    require((signature_count, chamber_count, row_width) == (SIGNATURES, CHAMBERS, PROFILE_BYTES), "profile header")
    expected_size = 20 + SIGNATURES * (8 + PROFILE_BYTES)
    require(len(raw) == expected_size, "profile truncation/trailing padding")
    dtype = np.dtype([("signature", "<u8"), ("payload", "u1", PROFILE_BYTES)])
    artifact = np.frombuffer(raw, dtype=dtype, offset=20, count=SIGNATURES)
    require(np.array_equal(artifact["signature"], np.asarray(universe, dtype=np.uint64)), "profile signature universe/order")
    require(np.array_equal(artifact["payload"], profiles), "complete packed profile bytes")

    profile_digest = sha256(b"diag3-row2599-edge39-label-profiles-v1\0")
    profile_counter = Counter()
    for signature, row in zip(universe, profiles, strict=True):
        payload = row.tobytes()
        profile_counter[payload] += 1
        profile_digest.update(signature.to_bytes(7, "little"))
        profile_digest.update(payload)
    unique_profiles = sorted(profile_counter)
    require(len(unique_profiles) == 10571, "canonical distinct profiles")
    profile_id = {payload: index for index, payload in enumerate(unique_profiles)}
    id_digest = sha256(b"edge39-referee-canonical-profile-ids-v1\0")
    for signature, row in zip(universe, profiles, strict=True):
        id_digest.update(signature.to_bytes(7, "little"))
        id_digest.update(profile_id[row.tobytes()].to_bytes(2, "little"))

    feasible_counts = np.empty(SIGNATURES, dtype=np.int32)
    transition_counts = np.empty(SIGNATURES, dtype=np.int16)
    for start in range(0, SIGNATURES, 2048):
        stop = min(SIGNATURES, start + 2048)
        bits = np.unpackbits(profiles[start:stop], axis=1, bitorder="little")
        feasible_counts[start:stop] = np.count_nonzero(bits, axis=1)
        transition_counts[start:stop] = np.count_nonzero(bits[:, 1:] != bits[:, :-1], axis=1)
    feasible_census = Counter(map(int, feasible_counts))
    transition_census = Counter(map(int, transition_counts))
    declared_profiles = certificate["signature_profiles"]
    require(declared_profiles["artifact_sha256"] == EXPECTED_PROFILE_SHA, "declared profile artifact")
    require(declared_profiles["packed_profile_bytes_each"] == PROFILE_BYTES, "declared profile width")
    require(declared_profiles["distinct_profiles"] == len(unique_profiles), "declared profile count")
    require(declared_profiles["semantic_sha256"] == profile_digest.hexdigest(), "declared profile semantic")
    require(declared_profiles["feasible_chamber_count_census"] == {str(k): v for k, v in sorted(feasible_census.items())}, "feasible-count census")
    require(declared_profiles["profile_transition_count_census"] == {str(k): v for k, v in sorted(transition_census.items())}, "transition-count census")
    require(declared_profiles["all_bad_loci_closed_by_incidence_rule"] is True, "bad-locus closure declaration")

    # Independent regular-path construction and incidence.
    zero = ["row2599:chart:0"]
    for index, event in enumerate(events):
        member = event["members"][0]
        zero.append(
            f"row2599:edge:039:event:{index:04d}:factor:{int(member['factor_id'])}:root:{int(member['root_index_within_factor'])}"
        )
    zero.append("row2599:chart:113")
    one = [f"row2599:edge:039:open:{index:04d}" for index in range(CHAMBERS)]
    require(len(zero) == len(set(zero)) == 5329 and len(one) == len(set(one)) == 5328, "stable regular cells")
    incidence = [(zero[i], one[i], -1, zero[i + 1], 1) for i in range(CHAMBERS)]
    require(len(incidence) == 5328, "signed path incidence")
    factor19069_cell = zero[5237]
    require(factor19069_cell == "row2599:edge:039:event:5236:factor:19069:root:0", "collar incidence cell")

    scope = certificate["scope"]
    require(scope == {
        "parent_index": 2599, "source_edge_index": 39, "source_chart": 0,
        "target_chart": 113, "generic_chambers": 5328,
        "signature_label_continuation": "COMPLETE_ON_ALL_OPEN_PATH_CHAMBERS",
        "wall_label_specialization": "CONSERVATIVE_ALL_INCIDENT_CHAMBERS_RULE",
        "global_parent_cell_coverage": "NOT_CLAIMED", "honest_9dvl_score": "2/9",
    }, "label scope")
    require(certificate["inputs"] == {
        "transition_path": TRANSITION_PATH,
        "transition_sha256": EXPECTED_TRANSITION_SHA,
        "point_bank_sha256": digest_file(POINT_BANK),
        "factor_census_sha256": digest_file(FACTOR_CENSUS),
    }, "label input pins")
    require(certificate["normalization"] == {
        "raw_extension_reorientation_mask": mask,
        "source_raw_normalized_label_sets_equal_after_reorientation": True,
    }, "normalization record")
    interface = certificate["edge_interface"]
    require(interface["stable_edge_key"] == "row2599:edge:039:charts:0-113", "label edge key")
    require(interface["cell_id_prefix"] == "row2599:edge:039", "label cell prefix")
    require(interface["profile_bits"] == "one bit per open chamber, increasing chamber index", "profile bit order")
    require(interface["signature_order"] == "ascending unsigned 56-bit row-2599 extension signature", "signature order")
    require(interface["collar_attachment"] == transition["edge_interface"]["collar_attachment"], "label/transition collar interface")
    require("no ledger promotion" in certificate["theorem_effect"], "theorem nonconsequence")
    payload = deepcopy(certificate)
    payload.pop("semantic_sha256")
    require(certificate["semantic_sha256"] == sha256(canonical(payload)).hexdigest(), "label semantic seal")

    # Edge-39-specific hostile mutations, applied to the frozen semantics.
    two_root_factor = next(
        int(event["members"][0]["factor_id"])
        for event in events if int(event["members"][0]["root_index_within_factor"]) == 1
    )
    deleted = [event for event in events if not (
        int(event["members"][0]["factor_id"]) == two_root_factor
        and int(event["members"][0]["root_index_within_factor"]) == 1
    )]
    require(len(deleted) != EVENTS, "two-root deletion canary survived")
    split_records = list(records)
    compound_index = next(i for i, event in enumerate(events) if int(event["members"][0]["occurrence_multiplicity"]) > 1)
    split_records.insert(compound_index, deepcopy(split_records[compound_index]))
    require(len(split_records) != EVENTS, "compound split canary survived")
    corrupt_profile = artifact["payload"].copy()
    corrupt_profile[0, 0] ^= np.uint8(1)
    require(not np.array_equal(corrupt_profile, profiles), "profile-bit canary survived")
    require(len(raw + b"\0") != expected_size, "profile trailing-padding canary survived")
    corrupt_terminal = set(raw_target)
    terminal_value = next(iter(corrupt_terminal))
    corrupt_terminal.remove(terminal_value)
    corrupt_terminal.add(terminal_value ^ 1)
    require(corrupt_terminal != labels, "terminal-label canary survived")
    corrupt_interface = deepcopy(interface)
    corrupt_interface["collar_attachment"]["event_index"] -= 1
    require(corrupt_interface != interface, "collar-index canary survived")
    corrupt_transition_interface = deepcopy(transition["edge_interface"])
    corrupt_transition_interface["orientation"] = "chart_113_to_chart_0"
    require(corrupt_transition_interface != transition["edge_interface"], "collar-orientation canary survived")
    corrupt_scope = deepcopy(scope)
    corrupt_scope["global_parent_cell_coverage"] = "COMPLETE"
    corrupt_scope["honest_9dvl_score"] = "3/9"
    require(corrupt_scope != scope, "global-scope canary survived")
    corrupt_cw = deepcopy(transition["regular_cw_path"])
    corrupt_cw["parent_infinity_subcomplex"] = ["row2599:chart:0"]
    require(corrupt_cw != transition["regular_cw_path"], "invented-infinity canary survived")

    print("PASS independent extension universe", SIGNATURES, universe_digest.hexdigest())
    print("PASS source and terminal raw labels", TOPES)
    print("PASS continuation", 5034, "simple +", 293, "compound events")
    print("PASS packed profiles", SIGNATURES, "x", PROFILE_BYTES, "bytes")
    print("PASS canonical profiles", len(unique_profiles), id_digest.hexdigest())
    print("PASS regular path", len(zero), "zero +", len(one), "one cells")
    print("PASS factor19069 collar cell", factor19069_cell)
    print("PASS 9 edge39-specific hostile mutations rejected")
    print("PROFILE_SEMANTIC_SHA256", profile_digest.hexdigest())
    print("LABEL_SEMANTIC_SHA256", certificate["semantic_sha256"])
    print("SCOPE local labelled edge/collar only; no global coverage or ledger change")


if __name__ == "__main__":
    main()
