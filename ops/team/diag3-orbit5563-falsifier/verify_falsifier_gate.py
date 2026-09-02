#!/usr/bin/env python3
"""Independent first-gate replay for the D3 orbit-5563 falsifier.

This checker reconstructs the framed-parent quotient directly from the
2,604 realizable chirotopes.  It deliberately does not import the existing
rank-drop atlas.  A frame is identified with another frame precisely when
their complete 70-bracket projective normalizations agree after the final
three column orientations are fixed canonically; this recovers the
projective/reorientation automorphism group of each unlabelled parent type.

The hard factor triple has trivial stabilizer, so every quotient class has
multiplicity equal to the parent automorphism-group order.  The exact sum of
all class multiplicities must be 104,993,280.

The second layer is fail-closed.  The open-cell sign and chart formulas are
transported symbolically, but the repository has no complete boundary atlas
and attachment proof over all parent realization spaces.  The expected
terminal outcome is therefore ``null``; no topology computation is allowed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import sys
import time

try:
    import resource
except ImportError:  # Not available on Windows.
    resource = None


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai/omreal"
CATALOG = OMREAL / "certs_4_8.jsonl"
EXTCOUNTS = ROOT / "ai/omgamma/data/extcount_4_9.jsonl"
QUOTIENT = HERE / "QUOTIENT_MANIFEST.json"
TRANSPORT = HERE / "TRANSPORT_CONTRACT.json"

SCHEMA = "diag3-orbit5563-falsifier-quotient-v1"
TRANSPORT_SCHEMA = "diag3-orbit5563-fullspace-transport-contract-v1"
BASE_REVISION = "bf6050ddc16e01dbff6da07d3d8c3ec31a9ab52f"
BASE_TREE = "4213fdb2adf5722d1b8a6b70aba4507e959fba6d"
PUBLISHED_GO = "9e578f6e9d094b3342ca474f0d188428dd44ae7a"
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL_ROW = (5_563, 4_373, 23_221)
PARENT_TYPES = 2_604
FRAMES = 40_320
RAW_PRESENTATIONS = 104_993_280

BASES = tuple(
    sorted(combinations(range(8), 4), key=lambda basis: tuple(reversed(basis)))
)
BASIS_INDEX = {basis: index for index, basis in enumerate(BASES)}
ALL_PARENTS = (1 << PARENT_TYPES) - 1

REQUIRED_STRATA = (
    "open_parent_points",
    "coordinate",
    "chart_divisor",
    "parent_wall",
    "singular_rank_drop",
    "occurrence_rank",
    "concurrence_rank",
    "extra_factor",
    "simultaneous_wall",
    "true_parent_infinity",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def semantic_digest(payload: dict) -> str:
    payload = dict(payload)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def negative_parity(values) -> bool:
    return bool(
        sum(
            values[left] > values[right]
            for left in range(len(values))
            for right in range(left + 1, len(values))
        )
        & 1
    )


def load_catalog():
    records = [
        json.loads(line)
        for line in CATALOG.read_text(encoding="ascii").splitlines()
        if line
    ]
    if len(records) != 2_628:
        raise AssertionError("the UOM(4,8) catalog size changed")
    realizable = []
    negative_by_basis = [0] * len(BASES)
    for source_index, record in enumerate(records):
        if record.get("n") != 8 or record.get("r") != 4:
            raise AssertionError("catalog rank or ground-set size changed")
        chi = record.get("chi", "")
        if len(chi) != 70 or set(chi) - {"+", "-"}:
            raise AssertionError("catalog is not uniform rank four")
        if record.get("verdict") != "REALIZABLE":
            continue
        parent_index = len(realizable)
        realizable.append((source_index, chi))
        for basis_index, value in enumerate(chi):
            if value == "-":
                negative_by_basis[basis_index] |= 1 << parent_index
    if len(realizable) != PARENT_TYPES:
        raise AssertionError("realizable parent census changed")
    return tuple(realizable), tuple(negative_by_basis)


def raw_negative(negative_by_basis, ordered_columns) -> int:
    basis = tuple(sorted(ordered_columns))
    sign = negative_by_basis[BASIS_INDEX[basis]]
    if negative_parity(ordered_columns):
        sign ^= ALL_PARENTS
    return sign


def frame_gauge(negative_by_basis, frame):
    denominator_sign = raw_negative(negative_by_basis, frame[:4])
    fifth_coordinate_signs = tuple(
        raw_negative(
            negative_by_basis,
            frame[:column] + (frame[4],) + frame[column + 1 : 4],
        )
        ^ denominator_sign
        for column in range(4)
    )
    gauge_sign = denominator_sign
    for value in fifth_coordinate_signs:
        gauge_sign ^= value
    return gauge_sign, fifth_coordinate_signs


def normalized_basis_sign(
    negative_by_basis, frame, positions, gauge_sign, fifth_coordinate_signs
):
    value = gauge_sign ^ raw_negative(
        negative_by_basis, tuple(frame[position] for position in positions)
    )
    for position in positions:
        if position < 4:
            value ^= fifth_coordinate_signs[position]
    return value & ALL_PARENTS


def canonical_frame_signs(negative_by_basis, frame):
    """Return all normalized signs modulo unfixed projective orientations.

    The first five columns determine the projective chart, but positions 5,
    6, and 7 retain independent column-orientation gauge.  Fix each by making
    bracket 012k positive.  Uniformity makes every anchor nonzero.
    """

    gauge_sign, fifth_signs = frame_gauge(negative_by_basis, frame)
    anchors = {
        position: normalized_basis_sign(
            negative_by_basis,
            frame,
            (0, 1, 2, position),
            gauge_sign,
            fifth_signs,
        )
        for position in range(5, 8)
    }
    answer = []
    for positions in BASES:
        value = normalized_basis_sign(
            negative_by_basis,
            frame,
            positions,
            gauge_sign,
            fifth_signs,
        )
        for position in positions:
            if position >= 5:
                value ^= anchors[position]
        answer.append(value & ALL_PARENTS)
    return tuple(answer)


def automorphism_masks(negative_by_basis, all_frames):
    identity = all_frames[0]
    reference = canonical_frame_signs(negative_by_basis, identity)

    digest = hashlib.sha256(b"diag3-orbit5563-parent-automorphism-masks-v1\0")
    byte_width = (PARENT_TYPES + 7) // 8
    masks = []
    for frame in all_frames:
        candidate = canonical_frame_signs(negative_by_basis, frame)
        matches = ALL_PARENTS
        for actual, expected in zip(candidate, reference, strict=True):
            matches &= ALL_PARENTS ^ (actual ^ expected)
            if not matches:
                break
        digest.update(matches.to_bytes(byte_width, "little"))
        masks.append(matches)
    if masks[0] != ALL_PARENTS:
        raise AssertionError("identity frame is not an automorphism of every parent")
    return tuple(masks), digest.hexdigest()


def compose(left, right):
    """Composition for frames viewed as maps position -> catalog label."""

    return tuple(left[right[position]] for position in range(8))


def inverse(frame):
    answer = [None] * 8
    for position, image in enumerate(frame):
        answer[image] = position
    return tuple(answer)


def verify_groups(automorphism_ranks, all_frames):
    identity = tuple(range(8))
    for parent_index, ranks in enumerate(automorphism_ranks):
        group = {all_frames[rank] for rank in ranks}
        if identity not in group:
            raise AssertionError(f"parent {parent_index} lost the identity")
        for element in group:
            if inverse(element) not in group:
                raise AssertionError(f"parent {parent_index} is not inverse-closed")
            for other in group:
                if compose(element, other) not in group:
                    raise AssertionError(f"parent {parent_index} is not closed")


def triple_stabilizer_ranks(all_frames):
    """Replay the target stabilizer from the pinned primitive-factor action."""

    sys.path.insert(0, str(OMREAL))
    import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: PLC0415

    occurrences, occurrence_factor, _polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    target = set(PRESENTATION)
    stabilizer = []
    for rank, frame in enumerate(all_frames):
        mapping = labeled.triple_map(frame)
        image = {
            labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for factor in PRESENTATION
        }
        if image == target:
            stabilizer.append(rank)
    if stabilizer != [0]:
        raise AssertionError(f"selected triple stabilizer changed: {stabilizer}")
    return stabilizer


def build_quotient_manifest():
    realizable, negative_by_basis = load_catalog()
    all_frames = tuple(permutations(range(8)))
    if len(all_frames) != FRAMES or all_frames[0] != tuple(range(8)):
        raise AssertionError("lexicographic S8 enumeration changed")

    masks, mask_digest = automorphism_masks(negative_by_basis, all_frames)
    automorphism_ranks = [[] for _ in range(PARENT_TYPES)]
    for frame_rank, mask in enumerate(masks):
        while mask:
            low_bit = mask & -mask
            automorphism_ranks[low_bit.bit_length() - 1].append(frame_rank)
            mask ^= low_bit
    automorphism_ranks = tuple(tuple(ranks) for ranks in automorphism_ranks)
    verify_groups(automorphism_ranks, all_frames)

    rows = []
    quotient_classes = 0
    multiplicity_sum = 0
    order_distribution = Counter()
    for parent_index, ((source_index, chi), ranks) in enumerate(
        zip(realizable, automorphism_ranks, strict=True)
    ):
        order = len(ranks)
        if not order or FRAMES % order:
            raise AssertionError(f"parent {parent_index} has invalid group order")
        classes = FRAMES // order
        quotient_classes += classes
        multiplicity_sum += classes * order
        order_distribution[order] += 1
        rows.append(
            {
                "parent_index": parent_index,
                "catalog_source_index": source_index,
                "chirotope_sha256": hashlib.sha256(chi.encode("ascii")).hexdigest(),
                "automorphism_frame_ranks": list(ranks),
                "automorphism_order": order,
                "quotient_class_count": classes,
                "multiplicity_of_each_class": order,
                "raw_frame_count": classes * order,
            }
        )
    if multiplicity_sum != RAW_PRESENTATIONS:
        raise AssertionError("quotient multiplicities do not recover the raw census")

    class_multiplicity_histogram = {
        order: parent_count * (FRAMES // order)
        for order, parent_count in sorted(order_distribution.items())
    }
    if (
        sum(class_multiplicity_histogram.values()) != quotient_classes
        or sum(
            multiplicity * classes
            for multiplicity, classes in class_multiplicity_histogram.items()
        )
        != RAW_PRESENTATIONS
    ):
        raise AssertionError("class-multiplicity histogram changed")

    chirotope_stream = hashlib.sha256(
        b"diag3-orbit5563-realizable-parent-stream-v1\0"
    )
    for source_index, chi in realizable:
        chirotope_stream.update(source_index.to_bytes(2, "little"))
        chirotope_stream.update(chi.encode("ascii"))
    automorphism_exceptions = [
        {
            "parent_index": row["parent_index"],
            "catalog_source_index": row["catalog_source_index"],
            "automorphism_frame_ranks": row["automorphism_frame_ranks"],
            "automorphism_order": row["automorphism_order"],
            "quotient_class_count": row["quotient_class_count"],
            "multiplicity_of_each_class": row["multiplicity_of_each_class"],
        }
        for row in rows
        if row["automorphism_order"] != 1
    ]

    triple_stabilizer = triple_stabilizer_ranks(all_frames)
    external_stabilizers = {
        row["i"]: row
        for row in map(
            json.loads,
            (line for line in EXTCOUNTS.read_text(encoding="utf-8").splitlines() if line),
        )
    }
    if set(external_stabilizers) != set(range(2_628)):
        raise AssertionError("external stabilizer cross-check index changed")
    if any(
        external_stabilizers[row["catalog_source_index"]]["stab"]
        != 2 * row["automorphism_order"]
        for row in rows
    ):
        raise AssertionError("independent parent automorphisms disagree with omgamma")
    payload = {
        "schema": SCHEMA,
        "track_id": "diag3-orbit5563-falsifier",
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "published_opening_go_revision": PUBLISHED_GO,
        "target": {
            "canonical_row": list(CANONICAL_ROW),
            "named_presentation": list(PRESENTATION),
        },
        "quotient_definition": {
            "raw_domain": "(realizable UOM(4,8) reorientation type, lexicographic S8 frame)",
            "equivalence": "left action of the exact projective/reorientation automorphism group of the parent; right action by the named-triple stabilizer",
            "parent_automorphism_test": "equality of all 70 signs after exact five-column projective normalization and canonical orientation of positions 5, 6, and 7 via brackets 012k",
            "class_model": "Aut(parent) \\ S8 / Stab(named factor triple)",
            "triple_stabilizer_frame_ranks": triple_stabilizer,
            "triple_stabilizer_order": len(triple_stabilizer),
            "class_multiplicity_rule": "Aut(parent) acts freely on frames; with trivial triple stabilizer every class has multiplicity |Aut(parent)|",
            "frame_rank_convention": "zero-based rank in itertools.permutations(range(8)) lexicographic order",
        },
        "source": {
            "catalog_path": "ai/omreal/certs_4_8.jsonl",
            "catalog_sha256": sha256(CATALOG),
            "redundant_stabilizer_crosscheck_path": "ai/omgamma/data/extcount_4_9.jsonl",
            "redundant_stabilizer_crosscheck_sha256": sha256(EXTCOUNTS),
            "redundant_stabilizer_crosscheck": "PASS 2,604/2,604; the full G' stabilizer order equals twice the independently reconstructed projective/reorientation automorphism order, with the factor two supplied by the sign-action kernel",
            "redundant_stabilizer_crosscheck_is_generator_oracle": False,
        },
        "parent_stream": {
            "catalog_source_indices": [source_index for source_index, _chi in realizable],
            "chirotope_stream_sha256": chirotope_stream.hexdigest(),
        },
        "automorphism_group_encoding": {
            "default": {
                "automorphism_frame_ranks": [0],
                "automorphism_order": 1,
                "quotient_class_count": FRAMES,
                "multiplicity_of_each_class": 1,
            },
            "default_parent_count": order_distribution[1],
            "exceptions": automorphism_exceptions,
            "exception_parent_count": len(automorphism_exceptions),
            "completeness_rule": "each parent index absent from exceptions uses the identity-only default; each listed exception gives every automorphism frame rank",
        },
        "totals": {
            "realizable_unlabelled_parent_types": len(rows),
            "frames_per_type": FRAMES,
            "raw_frame_parent_presentations": len(rows) * FRAMES,
            "quotient_classes": quotient_classes,
            "quotient_multiplicity_sum": multiplicity_sum,
            "automorphism_order_distribution": {
                str(order): count for order, count in sorted(order_distribution.items())
            },
            "quotient_class_multiplicity_histogram": {
                str(multiplicity): classes
                for multiplicity, classes in class_multiplicity_histogram.items()
            },
            "representative_matrices_are_full_realization_space_coverage": False,
        },
        "automorphism_mask_stream_sha256": mask_digest,
    }
    payload["semantic_sha256"] = semantic_digest(payload)
    return payload


def build_transport_contract(quotient):
    payload = {
        "schema": TRANSPORT_SCHEMA,
        "track_id": "diag3-orbit5563-falsifier",
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "quotient_manifest_semantic_sha256": quotient["semantic_sha256"],
        "quantified_domain": {
            "parent_types": PARENT_TYPES,
            "quotient_classes": quotient["totals"]["quotient_classes"],
            "raw_multiplicity": RAW_PRESENTATIONS,
            "points": "every point of every complete normalized realization space",
            "required_strata": list(REQUIRED_STRATA),
            "representative_matrix_promotion": "PROHIBITED",
        },
        "exact_open_cell_transport": {
            "status": "PASS",
            "scope": "every point of every uniform open normalized parent realization space and every framed quotient class",
            "sign_rule": "the sign of every normalized bracket is the catalog chirotope sign times the determinant-order parity and the four exact Cramer gauge signs",
            "chart_rule": "each ordered five-column projective frame is valid throughout a uniform parent space because every denominator is a nonzero parent bracket; transitions are rational Cramer maps localized only at those bracket units",
            "constancy_rule": "chirotope and denominator signs are constant on each realization space",
            "nonconsequence": "open-cell sign/chart transport gives neither a component partition nor closure or infinity coverage",
        },
        "obligations": [
            {
                "id": "Q1_EXACT_TYPE_FRAME_TRIPLE_QUOTIENT",
                "status": "PASS",
                "depends_on": [],
                "coverage": "all 2,604 types and all 40,320 frames; multiplicities sum to 104,993,280",
            },
            {
                "id": "Q2_OPEN_CELL_SIGN_AND_CHART_TRANSPORT",
                "status": "PASS",
                "depends_on": ["Q1_EXACT_TYPE_FRAME_TRIPLE_QUOTIENT"],
                "coverage": "all points in every uniform open normalized realization space",
            },
            {
                "id": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
                "status": "MISSING",
                "depends_on": ["Q2_OPEN_CELL_SIGN_AND_CHART_TRANSPORT"],
                "coverage": "no complete normalized compactification/stratum atlas exists for all parent types and quotient classes",
            },
            {
                "id": "Q4_COMPONENT_AND_RANK_DROP_ATTACHMENTS",
                "status": "BLOCKED_BY_Q3",
                "depends_on": ["Q3_COMPLETE_PARENT_BOUNDARY_ATLAS"],
                "coverage": "coordinate, singular/rank-drop, occurrence-rank, concurrence-rank, extra-factor, and simultaneous-wall attachments",
            },
            {
                "id": "Q5_TRUE_PARENT_INFINITY_TAGS",
                "status": "BLOCKED_BY_Q3",
                "depends_on": ["Q3_COMPLETE_PARENT_BOUNDARY_ATLAS"],
                "coverage": "sound distinction between true parent infinity and artificial chart/work boundaries",
            },
        ],
        "smallest_missing_obligation": {
            "id": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
            "reason": "the existing exact boundary stratification covers one named chart and explicitly disclaims a global primary decomposition or closure theorem",
            "required_artifact": "a complete finite normalized compactification atlas for every parent quotient class, with exact transition domains and exhaustive named boundary strata before component attachments are attempted",
        },
        "source_accounting": {
            "ai/omreal/PARENT_CONTRACTIBILITY_AUDIT.md": sha256(
                OMREAL / "PARENT_CONTRACTIBILITY_AUDIT.md"
            ),
            "ai/omreal/DIAG3_TRIPLE_BOUNDARY_STRATIFICATION.md": sha256(
                OMREAL / "DIAG3_TRIPLE_BOUNDARY_STRATIFICATION.md"
            ),
            "ai/omreal/data/DIAG3_triple_fullspace_feasibility_gate.json": sha256(
                OMREAL / "data/DIAG3_triple_fullspace_feasibility_gate.json"
            ),
            "ai/omreal/verify_diag3_triple_rank_drop_parent_atlas.py": sha256(
                OMREAL / "verify_diag3_triple_rank_drop_parent_atlas.py"
            ),
            "ai/omreal/verify_diag3_triple_factor_orbits.py": sha256(
                OMREAL / "verify_diag3_triple_factor_orbits.py"
            ),
        },
        "canary_policy": {
            "artificial_boundaries_are_true_infinity": False,
            "stored_representative_is_complete_cell_coverage": False,
            "one_chart_is_complete_boundary_coverage": False,
            "omitted_required_stratum_is_acceptable": False,
            "duplicate_or_missing_quotient_transport_is_acceptable": False,
        },
        "first_gate": {
            "layer_1_quotient_manifest": "COMPLETE",
            "layer_2_full_space_transport_and_attachment": "INCOMPLETE_AT_BOUNDARY_ATLAS",
            "classification": "null",
            "topology_computation_authorized": False,
            "count_change": 0,
            "ledger_change": "NONE",
            "mandatory_strategy": "PIVOT; do not resume local box, collar, macrobox, or clipped-wall continuation",
        },
    }
    payload["semantic_sha256"] = semantic_digest(payload)
    return payload


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_quotient_structure(manifest):
    require(manifest["schema"] == SCHEMA, "quotient schema")
    sources = manifest["parent_stream"]["catalog_source_indices"]
    require(len(sources) == PARENT_TYPES, "parent source census")
    require(len(set(sources)) == PARENT_TYPES, "duplicate parent source")
    encoding = manifest["automorphism_group_encoding"]
    default = encoding["default"]
    require(
        default
        == {
            "automorphism_frame_ranks": [0],
            "automorphism_order": 1,
            "quotient_class_count": FRAMES,
            "multiplicity_of_each_class": 1,
        },
        "identity-only default encoding",
    )
    exceptions = {row["parent_index"]: row for row in encoding["exceptions"]}
    require(len(exceptions) == len(encoding["exceptions"]), "duplicate exception")
    require(
        encoding["exception_parent_count"] == len(exceptions)
        and encoding["default_parent_count"] == PARENT_TYPES - len(exceptions),
        "default/exception parent count",
    )
    raw = 0
    classes = 0
    for index, source_index in enumerate(sources):
        row = exceptions.get(index, default)
        if index in exceptions:
            require(row["catalog_source_index"] == source_index, "exception source")
        order = row["automorphism_order"]
        require(row["automorphism_frame_ranks"][0] == 0, "identity canary")
        require(len(row["automorphism_frame_ranks"]) == order, "group-order list")
        require(len(set(row["automorphism_frame_ranks"])) == order, "duplicate automorphism")
        require(FRAMES % order == 0, "orbit-stabilizer divisibility")
        require(row["quotient_class_count"] == FRAMES // order, "class count")
        require(row["multiplicity_of_each_class"] == order, "class multiplicity")
        classes += row["quotient_class_count"]
        raw += row["quotient_class_count"] * row["multiplicity_of_each_class"]
    totals = manifest["totals"]
    require(raw == RAW_PRESENTATIONS, "raw quotient multiplicity sum")
    require(totals["quotient_classes"] == classes, "quotient class total")
    require(totals["quotient_multiplicity_sum"] == raw, "stored multiplicity total")
    histogram = {
        int(multiplicity): count
        for multiplicity, count in totals[
            "quotient_class_multiplicity_histogram"
        ].items()
    }
    require(sum(histogram.values()) == classes, "multiplicity histogram classes")
    require(
        sum(multiplicity * count for multiplicity, count in histogram.items())
        == raw,
        "multiplicity histogram raw sum",
    )
    require(
        totals["representative_matrices_are_full_realization_space_coverage"]
        is False,
        "representative-matrix scope guard",
    )
    require(
        manifest["quotient_definition"]["triple_stabilizer_frame_ranks"] == [0],
        "hard-triple stabilizer",
    )
    require(manifest["semantic_sha256"] == semantic_digest(manifest), "quotient semantic")


def validate_transport(contract, quotient):
    require(contract["schema"] == TRANSPORT_SCHEMA, "transport schema")
    require(
        contract["quotient_manifest_semantic_sha256"]
        == quotient["semantic_sha256"],
        "transport quotient binding",
    )
    require(
        tuple(contract["quantified_domain"]["required_strata"]) == REQUIRED_STRATA,
        "required-stratum census",
    )
    require(
        contract["quantified_domain"]["representative_matrix_promotion"]
        == "PROHIBITED",
        "representative promotion guard",
    )
    obligations = {row["id"]: row for row in contract["obligations"]}
    require(
        tuple(obligations)
        == (
            "Q1_EXACT_TYPE_FRAME_TRIPLE_QUOTIENT",
            "Q2_OPEN_CELL_SIGN_AND_CHART_TRANSPORT",
            "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
            "Q4_COMPONENT_AND_RANK_DROP_ATTACHMENTS",
            "Q5_TRUE_PARENT_INFINITY_TAGS",
        ),
        "obligation order/census",
    )
    require(obligations["Q1_EXACT_TYPE_FRAME_TRIPLE_QUOTIENT"]["status"] == "PASS", "Q1")
    require(obligations["Q2_OPEN_CELL_SIGN_AND_CHART_TRANSPORT"]["status"] == "PASS", "Q2")
    require(obligations["Q3_COMPLETE_PARENT_BOUNDARY_ATLAS"]["status"] == "MISSING", "Q3")
    require(obligations["Q4_COMPONENT_AND_RANK_DROP_ATTACHMENTS"]["status"] == "BLOCKED_BY_Q3", "Q4")
    require(obligations["Q5_TRUE_PARENT_INFINITY_TAGS"]["status"] == "BLOCKED_BY_Q3", "Q5")
    require(
        contract["smallest_missing_obligation"]["id"]
        == "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
        "smallest missing obligation",
    )
    policy = contract["canary_policy"]
    require(not any(policy.values()), "hostile scope canary accepted")
    gate = contract["first_gate"]
    require(gate["layer_1_quotient_manifest"] == "COMPLETE", "layer 1")
    require(
        gate["layer_2_full_space_transport_and_attachment"]
        == "INCOMPLETE_AT_BOUNDARY_ATLAS",
        "layer 2",
    )
    require(gate["classification"] == "null", "terminal classification")
    require(gate["topology_computation_authorized"] is False, "topology stop")
    require(gate["count_change"] == 0 and gate["ledger_change"] == "NONE", "accounting")
    for relative, expected in contract["source_accounting"].items():
        require(sha256(ROOT / relative) == expected, f"source digest {relative}")
    require(contract["semantic_sha256"] == semantic_digest(contract), "transport semantic")


def hostile_canaries(quotient, contract):
    corrupt = deepcopy(quotient)
    corrupt["totals"]["quotient_class_multiplicity_histogram"]["1"] -= 1
    try:
        validate_quotient_structure(corrupt)
    except AssertionError:
        pass
    else:
        raise AssertionError("missing quotient multiplicity canary survived")

    corrupt = deepcopy(quotient)
    corrupt["automorphism_group_encoding"]["exceptions"][0][
        "automorphism_frame_ranks"
    ].pop(0)
    try:
        validate_quotient_structure(corrupt)
    except (AssertionError, IndexError):
        pass
    else:
        raise AssertionError("missing identity automorphism canary survived")

    corrupt = deepcopy(contract)
    corrupt["canary_policy"]["artificial_boundaries_are_true_infinity"] = True
    try:
        validate_transport(corrupt, quotient)
    except AssertionError:
        pass
    else:
        raise AssertionError("false infinity canary survived")

    corrupt = deepcopy(contract)
    corrupt["quantified_domain"]["required_strata"].remove("singular_rank_drop")
    try:
        validate_transport(corrupt, quotient)
    except AssertionError:
        pass
    else:
        raise AssertionError("omitted singular stratum canary survived")

    corrupt = deepcopy(contract)
    corrupt["quantified_domain"]["representative_matrix_promotion"] = "ALLOWED"
    try:
        validate_transport(corrupt, quotient)
    except AssertionError:
        pass
    else:
        raise AssertionError("representative-matrix promotion canary survived")


def write_json(path, payload):
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()

    rebuilt = build_quotient_manifest()
    rebuilt_transport = build_transport_contract(rebuilt)
    if args.generate:
        write_json(QUOTIENT, rebuilt)
        write_json(TRANSPORT, rebuilt_transport)
    quotient = json.loads(QUOTIENT.read_text(encoding="utf-8"))
    contract = json.loads(TRANSPORT.read_text(encoding="utf-8"))
    require(quotient == rebuilt, "stored quotient differs from independent rebuild")
    require(contract == rebuilt_transport, "stored transport contract differs from rebuild")
    validate_quotient_structure(quotient)
    validate_transport(contract, quotient)
    hostile_canaries(quotient, contract)

    totals = quotient["totals"]
    print(
        "PASS exact parent/frame/triple quotient",
        f"parents={PARENT_TYPES}",
        f"frames={FRAMES}",
        f"classes={totals['quotient_classes']}",
    )
    print(
        "PASS quotient multiplicities",
        f"sum={totals['quotient_multiplicity_sum']}/{RAW_PRESENTATIONS}",
    )
    print(
        "PASS class-multiplicity histogram",
        totals["quotient_class_multiplicity_histogram"],
    )
    print("PASS hard triple stabilizer is identity")
    print("PASS exact open-cell sign/chart transport formula for every point")
    print("PASS hostile canaries: missing/duplicate transport, false infinity, omitted stratum, representative promotion")
    print("NULL complete parent-boundary atlas and attachments are missing")
    print("STOP no topology computation authorized; ledger and row counts unchanged")
    print("QUOTIENT_SEMANTIC", quotient["semantic_sha256"])
    print("TRANSPORT_SEMANTIC", contract["semantic_sha256"])
    print(
        "RESOURCE",
        f"elapsed_seconds={time.monotonic() - started:.3f}",
        f"peak_rss_kib={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource is not None else 'unavailable'}",
    )


if __name__ == "__main__":
    main()
