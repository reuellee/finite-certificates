#!/usr/bin/env python3
"""Replay the D3 orbit-5563 prover's terminal first-gate NULL.

This checker reconstructs the complete type/frame/diagonal-S8 quotient from
the pinned UOM(4,8) catalog and the authenticated residual-factor action.  It
also verifies the deliberately fail-closed transport contract: interior sign,
chart, and relabeling transport are proved, while complete closure-stratum
transport and true-infinity attachment remain missing.  No topology search is
performed or accepted by this checker.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
from itertools import permutations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
OMGAMMA = ROOT / "ai" / "omgamma"
sys.path.insert(0, str(OMREAL))
sys.path.insert(0, str(OMGAMMA))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
from canon import _sign_kernel, canonical as canonical_chirotope  # noqa: E402
from core import from_string as chirotope_from_string  # noqa: E402


SCHEMA = "diag3-orbit5563-type-frame-s8-quotient-v1"
TRANSPORT_SCHEMA = "diag3-orbit5563-fullspace-transport-contract-v1"
CANARY_SCHEMA = "diag3-orbit5563-first-gate-canaries-v1"
REPLAY_SCHEMA = "diag3-orbit5563-prover-replay-manifest-v1"
GROUP_ORDER = 40_320
CATALOG_RECORDS = 2_628
REALIZABLE_TYPES = 2_604
RAW_GAUGE_REPRESENTATIVES = 104_993_280
QUOTIENT_CLASSES = 100_086_840
EXPANDED_SIMULTANEOUS_DOMAIN = 4_035_501_388_800
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL_ROW = (5_563, 4_373, 23_221)
NAMED_TO_CANONICAL = (5, 1, 4, 7, 2, 3, 0, 6)

CATALOG = OMREAL / "certs_4_8.jsonl"
MANIFEST = HERE / "TYPE_FRAME_S8_QUOTIENT_MANIFEST.json"
TRANSPORT = HERE / "TRANSPORT_CONTRACT.json"
CANARIES = HERE / "CANARIES.json"
REPLAY = HERE / "REPLAY_MANIFEST.json"

PINNED_SHA256 = {
    "ai/omreal/certs_4_8.jsonl": (
        "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b"
    ),
    "ai/omreal/DIAG3_TRIPLE_FACTOR_REDUCTION.md": (
        "805ed958909097234d05f5e2c0ec65364ecf394cd1bca0422cf70faa3d09c5cd"
    ),
    "ai/omreal/PARENT_CONTRACTIBILITY_AUDIT.md": (
        "d0fde0f211db71228a48af3c928a213181bab4bb29c25a57d2ed7417f49de226"
    ),
    "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md": (
        "0a372197a49f4a767c06b23a6df830ef2784e7fe653b4b3eb1a506eec0518e27"
    ),
    "ai/omreal/data/DIAG3_triple_fullspace_feasibility_gate.json": (
        "8ad62abdd3bd7d9bc14e5bfec3e407f3c07fd740a5475d1243e8dbb9e08d8692"
    ),
    "ops/team/clipped-wall-prover/RESULT.yaml": (
        "8f33a354f55e141aa53fe9253537c7caac385accf29c890865747de8982d1352"
    ),
    "ops/team/clipped-wall-falsifier/RESULT.yaml": (
        "8ceb928968875e314b38f0457eda99e1e51a557e675cd7beaf20798f7ae5957f"
    ),
    "ai/omgamma/canon.py": (
        "17ca82b8bf34b0d0c9e5b5c52111ee44d16461c636682cd17762d9eb2e99aa7e"
    ),
    "ai/omgamma/core.py": (
        "6f0d256025c0b465231ca413c62752b63d06af85be7bba628f4e72e6e0a98dcc"
    ),
}


class GateError(AssertionError):
    """Expected fail-closed validation error."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def semantic_seal(payload: dict) -> str:
    unsealed = dict(payload)
    unsealed.pop("semantic_sha256", None)
    return hashlib.sha256(canonical_bytes(unsealed)).hexdigest()


def seal(payload: dict) -> dict:
    answer = copy.deepcopy(payload)
    answer["semantic_sha256"] = semantic_seal(answer)
    return answer


def verify_pinned_sources() -> None:
    for relative, expected in PINNED_SHA256.items():
        actual = sha256_file(ROOT / relative)
        if actual != expected:
            raise GateError(f"pinned source changed: {relative}: {actual}")


def load_catalog_entries() -> list[dict]:
    raw_lines = CATALOG.read_bytes().splitlines()
    if len(raw_lines) != CATALOG_RECORDS:
        raise GateError("catalog record census changed")
    sign_kernel = _sign_kernel(8, 4)
    if sign_kernel != ((255, 0),):
        raise GateError("rank-four/eight sign-action kernel changed")
    sign_kernel_order = 1 << len(sign_kernel)
    entries = []
    canonical_keys = set()
    for source_index, raw_line in enumerate(raw_lines):
        record = json.loads(raw_line)
        if record.get("n") != 8 or record.get("r") != 4:
            raise GateError("catalog rank or ground-set size changed")
        chi = record.get("chi", "")
        if len(chi) != 70 or set(chi) - {"+", "-"}:
            raise GateError("catalog chirotope encoding changed")
        if record.get("verdict") != "REALIZABLE":
            continue
        matrix = record.get("matrix")
        if (
            not isinstance(matrix, list)
            or len(matrix) != 4
            or any(not isinstance(row, list) or len(row) != 8 for row in matrix)
        ):
            raise GateError("realizable catalog entry lost its 4x8 witness")
        canonical = canonical_chirotope(
            8,
            4,
            chirotope_from_string(8, 4, chi),
            want_witness=False,
        )
        canonical_key = canonical["canmask"]
        if canonical_key in canonical_keys:
            raise GateError("realizable catalog types are not distinct")
        canonical_keys.add(canonical_key)
        automorphism_order = canonical["nstates"]
        full_stabilizer_order = canonical["stab_order_exact"]
        if (
            full_stabilizer_order
            != sign_kernel_order * automorphism_order
            or GROUP_ORDER % automorphism_order
        ):
            raise GateError("parent stabilizer projection reconciliation changed")
        quotient_class_count = GROUP_ORDER // automorphism_order
        ordinal = len(entries)
        entries.append(
            {
                "type_ordinal": ordinal,
                "catalog_record_index": source_index,
                "catalog_record_sha256": hashlib.sha256(raw_line).hexdigest(),
                "chirotope_sha256": hashlib.sha256(
                    chi.encode("ascii")
                ).hexdigest(),
                "matrix_canonical_sha256": hashlib.sha256(
                    canonical_bytes(matrix)
                ).hexdigest(),
                "reorientation_canonical_sha256": hashlib.sha256(
                    canonical_key.to_bytes(9, "little")
                ).hexdigest(),
                "canonicalizer_color_count": canonical["ncolors"],
                "sign_action_kernel_order": sign_kernel_order,
                "full_reorientation_label_stabilizer_order": (
                    full_stabilizer_order
                ),
                "projected_parent_automorphism_order": automorphism_order,
                "frame_rank_interval": [0, GROUP_ORDER],
                "quotient_class_count": quotient_class_count,
                "raw_multiplicity_per_quotient_class": automorphism_order,
                "raw_multiplicity_contribution": (
                    quotient_class_count * automorphism_order
                ),
            }
        )
    if len(entries) != REALIZABLE_TYPES:
        raise GateError("realizable parent-type census changed")
    return entries


def group_action_data() -> dict:
    occurrences, occurrence_factor, _polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    target = frozenset(PRESENTATION)
    identity = tuple(range(8))
    stabilizer = []
    images = set()
    frame_digest = hashlib.sha256(
        b"diag3-orbit5563-lexicographic-s8-frames-v1\0"
    )
    orbit_digest = hashlib.sha256(
        b"diag3-orbit5563-hard-triple-orbit-v1\0"
    )
    frame_count = 0
    for frame in permutations(range(8)):
        frame_count += 1
        frame_digest.update(bytes(frame))
        mapping = labeled.triple_map(frame)
        image = tuple(
            sorted(
                labeled.transform_factor(
                    factor, mapping, factor_occurrence, occurrence_factor
                )
                for factor in PRESENTATION
            )
        )
        images.add(image)
        orbit_digest.update((",".join(map(str, image)) + "\n").encode("ascii"))
        if frozenset(image) == target:
            stabilizer.append(frame)
    if frame_count != GROUP_ORDER:
        raise GateError("S8 frame enumeration changed")
    if stabilizer != [identity]:
        raise GateError("hard presentation stabilizer is not the identity")
    if len(images) != GROUP_ORDER:
        raise GateError("hard presentation orbit is not an S8 torsor")

    named_mapping = labeled.triple_map(NAMED_TO_CANONICAL)
    named_image = tuple(
        labeled.transform_factor(
            factor, named_mapping, factor_occurrence, occurrence_factor
        )
        for factor in PRESENTATION
    )
    if set(named_image) != set(CANONICAL_ROW):
        raise GateError("named presentation no longer maps to canonical row")
    return {
        "name": "S8",
        "order": GROUP_ORDER,
        "frame_enumeration": "itertools.permutations(range(8)), lexicographic",
        "frame_enumeration_sha256": frame_digest.hexdigest(),
        "selected_presentation": list(PRESENTATION),
        "selected_stabilizer": [list(identity)],
        "selected_stabilizer_order": 1,
        "selected_orbit_size": GROUP_ORDER,
        "selected_orbit_enumeration_sha256": orbit_digest.hexdigest(),
        "canonical_row": list(CANONICAL_ROW),
        "named_to_canonical_permutation_zero_based": list(NAMED_TO_CANONICAL),
        "named_to_canonical_image": list(named_image),
    }


def expected_manifest() -> dict:
    entries = load_catalog_entries()
    group = group_action_data()
    compact_entries = [
        [
            entry["catalog_record_index"],
            entry["projected_parent_automorphism_order"],
            entry["quotient_class_count"],
        ]
        for entry in entries
    ]
    detailed_reconciliation_sha256 = hashlib.sha256(
        canonical_bytes(entries)
    ).hexdigest()
    automorphism_histogram = {}
    raw_multiplicity_histogram = {}
    raw_contribution_histogram = {}
    quotient_classes = 0
    raw_multiplicity_sum = 0
    for entry in entries:
        order = entry["projected_parent_automorphism_order"]
        class_count = entry["quotient_class_count"]
        raw_contribution = entry["raw_multiplicity_contribution"]
        automorphism_histogram[order] = automorphism_histogram.get(order, 0) + 1
        raw_multiplicity_histogram[order] = (
            raw_multiplicity_histogram.get(order, 0) + class_count
        )
        raw_contribution_histogram[order] = (
            raw_contribution_histogram.get(order, 0) + raw_contribution
        )
        quotient_classes += class_count
        raw_multiplicity_sum += raw_contribution
    if quotient_classes != QUOTIENT_CLASSES:
        raise GateError("quotient class count changed")
    if raw_multiplicity_sum != RAW_GAUGE_REPRESENTATIVES:
        raise GateError("raw multiplicity sum changed")
    payload = {
        "schema": SCHEMA,
        "cycle_id": "2026-08-30-diag3-orbit5563-global-exit",
        "track_id": "diag3-orbit5563-prover",
        "signed_opening": {
            "local_commit": "bf6050ddc16e01dbff6da07d3d8c3ec31a9ab52f",
            "published_commit": "9e578f6e9d094b3342ca474f0d188428dd44ae7a",
            "content_tree": "4213fdb2adf5722d1b8a6b70aba4507e959fba6d",
            "verdict": "GO",
        },
        "group": group,
        "quotient_definition": {
            "unlabelled_parent_types": REALIZABLE_TYPES,
            "raw_parent_frames_per_type": GROUP_ORDER,
            "hard_triple_orbit_size": GROUP_ORDER,
            "expanded_simultaneous_domain_total": EXPANDED_SIMULTANEOUS_DOMAIN,
            "labeled_parent_orbit_for_type_T": "S8/Aut(T)",
            "simultaneous_domain_for_type_T": "(S8/Aut(T)) x (S8.P)",
            "diagonal_action": (
                "h.(T,[f],g.P)=(T,[h*f],(h*g).P), with left composition in S8"
            ),
            "freeness_reason": (
                "if h fixes a simultaneous pair then h fixes g.P; the hard-triple "
                "stabilizer is identity"
            ),
            "gauge_slice": "the triple coordinate equals P=(5563,16134,19284)",
            "gauge_map": "(T,[f],g.P) maps to (T,[g^{-1}*f],P)",
            "existence_reason": "apply g^{-1} to any simultaneous pair",
            "uniqueness_reason": (
                "two gauge choices differ by an element stabilizing P, hence "
                "by identity"
            ),
            "per_type_class_formula": "40320 / |Aut(T)|",
            "per_class_raw_multiplicity_formula": "|Aut(T)|",
            "number_of_quotient_classes": quotient_classes,
            "sum_of_raw_multiplicities": raw_multiplicity_sum,
            "raw_frame_parent_sanity_census": RAW_GAUGE_REPRESENTATIVES,
            "raw_frame_rule": (
                "The governed raw domain retains all 40320 frames per type, "
                "but frames in one right Aut(T)-coset represent the same "
                "quotient class."
            ),
            "sign_action_kernel_order": 2,
            "parent_type_automorphism_order_histogram": {
                str(key): automorphism_histogram[key]
                for key in sorted(automorphism_histogram)
            },
            "quotient_class_raw_multiplicity_histogram": {
                str(key): raw_multiplicity_histogram[key]
                for key in sorted(raw_multiplicity_histogram)
            },
            "raw_multiplicity_contribution_histogram": {
                str(key): raw_contribution_histogram[key]
                for key in sorted(raw_contribution_histogram)
            },
            "burnside_reconciliation": (
                "For the free right action of Aut(T) on S8 frames, only its "
                "identity fixes a frame, so Burnside gives 40320/|Aut(T)| "
                "classes; each class has |Aut(T)| raw frames. The hard-triple "
                "identity stabilizer separately proves the simultaneous "
                "diagonal S8 orbit has size 40320."
            ),
        },
        "catalog": {
            "path": "ai/omreal/certs_4_8.jsonl",
            "sha256": PINNED_SHA256["ai/omreal/certs_4_8.jsonl"],
            "records": CATALOG_RECORDS,
            "realizable_unlabelled_types": REALIZABLE_TYPES,
            "entry_columns": [
                "catalog_record_index",
                "projected_parent_automorphism_order_or_raw_multiplicity",
                "quotient_class_count",
            ],
            "entry_row_rule": (
                "Row ordinal is the realizable type ordinal; raw contribution "
                "is column[1]*column[2]=40320; the pinned catalog row supplies "
                "the chirotope and matrix."
            ),
            "detailed_reconciliation_sha256": detailed_reconciliation_sha256,
            "entries": compact_entries,
        },
        "coverage": {
            "included": (
                "Every one of the 2604 realizable unlabelled UOM(4,8) types; "
                "every lexicographic S8 frame rank 0..40319; and every hard-"
                "triple orbit label modulo the exact diagonal S8 action."
            ),
            "quotient_classes": quotient_classes,
            "sum_raw_multiplicities": raw_multiplicity_sum,
            "uncovered_raw_frame_presentations": 0,
            "representative_matrix_nonconsequence": (
                "The stored matrix authenticates the type and finite sign "
                "census only; it does not cover its realization space, "
                "components, rank drops, closure, or infinity."
            ),
        },
    }
    return seal(payload)


def expected_transport() -> dict:
    payload = {
        "schema": TRANSPORT_SCHEMA,
        "cycle_id": "2026-08-30-diag3-orbit5563-global-exit",
        "track_id": "diag3-orbit5563-prover",
        "manifest_schema": SCHEMA,
        "terminal_classification": "null",
        "layer_1_quotient_manifest": "PASS_COMPLETE_EXACT",
        "layer_2_fullspace_transport": "FAIL_CLOSED_MISSING_CLOSURE_STRATA",
        "proved_transport": {
            "uniform_interior_parent_signs": {
                "status": "PROVED_FOR_ALL_POINTS",
                "quantifier": (
                    "For every manifest type T, every frame f in S8, every "
                    "point x of the complete open normalized realization "
                    "space X_T, and every 4-subset bracket."
                ),
                "argument": (
                    "X_T is the realization space of one fixed uniform "
                    "chirotope, so every bracket is nonzero with its fixed "
                    "chirotope sign at every x; frame relabeling contributes "
                    "only the exact permutation parity."
                ),
            },
            "uniform_interior_frame_charts": {
                "status": "PROVED_FOR_ALL_POINTS",
                "quantifier": (
                    "For every manifest type T, every frame f in S8, and "
                    "every x in X_T."
                ),
                "argument": (
                    "Uniformity makes the first four frame columns a basis "
                    "and all four replacement minors for the fifth column "
                    "nonzero. Exact Cramer normalization therefore defines "
                    "the stated frame chart at every interior point."
                ),
            },
            "diagonal_factor_formula_equivariance": {
                "status": "PROVED_EXACT",
                "quantifier": (
                    "For every h in S8 and every residual-factor occurrence "
                    "in the authenticated factor action."
                ),
                "argument": (
                    "The occurrence-to-primitive-factor map is checked to be "
                    "well defined under labeled.triple_map(h); simultaneous "
                    "relabeling transports the parent frame and all three "
                    "factor formulas together."
                ),
            },
        },
        "missing_transport": {
            "status": "MISSING",
            "smallest_missing_object_id": (
                "all_parent_closure_stratum_transport_and_attachment_atlas"
            ),
            "exact_obligation": (
                "For every manifest pair (T,f), supply a complete exact "
                "stratified Hausdorff compactification Xbar_(T,f), charts "
                "covering every required closure stratum, and transition/"
                "attachment maps commuting with the S8 factor transport; "
                "each parent-wall, chart-divisor, coordinate, rank-drop, "
                "extra-factor, simultaneous-wall, and true-infinity point "
                "must be covered and true infinity distinguished from every "
                "artificial work boundary."
            ),
            "uncovered_quantifier": (
                "The union, over every one of the 2604 types and all 40320 "
                "frames, of every required closure stratum and its residual-"
                "triple attachment in Xbar_(T,f)\\X_(T,f). No member of this "
                "global union is promoted from a stored representative "
                "matrix or a local box."
            ),
            "attachment_artifacts": [],
            "why_existing_inputs_do_not_fill_it": [
                (
                    "PARENT_CONTRACTIBILITY_AUDIT.md proves interior "
                    "contractibility, not a complete compactification or its "
                    "strata."
                ),
                (
                    "DIAG3_TRIPLE_BOUNDARY_STRATIFICATION.md is exact only at "
                    "its declared symbolic/local scope and makes no complete "
                    "all-parent closure claim."
                ),
                (
                    "The pinned fullspace feasibility gate is FAIL_CLOSED and "
                    "still requires a complete critical census plus frontier "
                    "attachments."
                ),
            ],
        },
        "scope_guards": {
            "representative_matrix_covers_full_realization_space": False,
            "artificial_scope_boundary_is_true_parent_infinity": False,
            "macrobox20_3468_attachment_accepted": False,
            "topology_computation_permitted_after_this_gate": False,
            "component_or_infinity_claim_permitted": False,
            "row_count_before": 1_162_302,
            "row_count_after": 1_162_302,
            "ledger_change_recommended": "none",
            "mandatory_next_strategy": "PIVOT",
        },
        "source_sha256": PINNED_SHA256,
    }
    return seal(payload)


def expected_canaries() -> dict:
    return {
        "schema": CANARY_SCHEMA,
        "fixtures": [
            {
                "id": "complete_manifest",
                "class": "positive",
                "expected": "ACCEPT_COMPLETE_QUOTIENT",
            },
            {
                "id": "complete_manifest_missing_transport",
                "class": "null",
                "expected": "ACCEPT_TERMINAL_NULL",
            },
            {
                "id": "drop_one_raw_multiplicity_resealed",
                "class": "hostile",
                "expected_error": "raw multiplicity sum changed",
            },
            {
                "id": "force_parent_automorphism_identity_resealed",
                "class": "hostile",
                "expected_error": "parent automorphism reconciliation changed",
            },
            {
                "id": "claim_nontrivial_hard_stabilizer_resealed",
                "class": "hostile",
                "expected_error": "hard presentation stabilizer claim changed",
            },
            {
                "id": "promote_representative_matrix_resealed",
                "class": "hostile",
                "expected_error": "representative-matrix promotion prohibited",
            },
            {
                "id": "close_transport_without_attachment_resealed",
                "class": "hostile",
                "expected_error": "closure transport cannot pass without attachment artifacts",
            },
            {
                "id": "artificial_scope_boundary_as_infinity",
                "class": "hostile",
                "expected_error": "artificial scope boundary is not true parent infinity",
            },
            {
                "id": "macrobox20_attachment_false",
                "class": "negative",
                "expected": "ACCEPT_PINNED_FALSE_ATTACHMENT",
            },
            {
                "id": "omitted_component",
                "class": "hostile",
                "expected_error": "topology prohibited at terminal first-gate null",
            },
            {
                "id": "unsound_edge",
                "class": "hostile",
                "expected_error": "topology prohibited at terminal first-gate null",
            },
            {
                "id": "positive_exit",
                "class": "positive",
                "expected_error": "topology prohibited at terminal first-gate null",
            },
            {
                "id": "compact_component",
                "class": "negative",
                "expected_error": "topology prohibited at terminal first-gate null",
            },
        ],
    }


def expected_replay_manifest(
    manifest: dict, contract: dict, canaries: dict
) -> dict:
    payload = {
        "schema": REPLAY_SCHEMA,
        "cycle_id": "2026-08-30-diag3-orbit5563-global-exit",
        "track_id": "diag3-orbit5563-prover",
        "terminal_classification": "null",
        "replay_command": (
            "PYTHONDONTWRITEBYTECODE=1 python3 "
            "ops/team/diag3-orbit5563-prover/"
            "verify_diag3_orbit5563_prover.py"
        ),
        "expected_exit": 0,
        "expected_summary": {
            "realizable_unlabelled_types": REALIZABLE_TYPES,
            "raw_frames_per_type": GROUP_ORDER,
            "number_of_quotient_classes": QUOTIENT_CLASSES,
            "sum_of_raw_multiplicities": RAW_GAUGE_REPRESENTATIVES,
            "parent_type_automorphism_order_histogram": manifest[
                "quotient_definition"
            ]["parent_type_automorphism_order_histogram"],
            "quotient_class_raw_multiplicity_histogram": manifest[
                "quotient_definition"
            ]["quotient_class_raw_multiplicity_histogram"],
            "selected_stabilizer_order": 1,
            "selected_orbit_size": GROUP_ORDER,
            "manifest_semantic_sha256": manifest["semantic_sha256"],
            "transport_semantic_sha256": contract["semantic_sha256"],
            "canaries_passed": len(canaries["fixtures"]),
            "topology_computation": "NOT_RUN",
            "row_count_after": 1_162_302,
            "ledger_change": "none",
            "next_strategy": "PIVOT",
        },
        "artifact_sha256": {
            "TYPE_FRAME_S8_QUOTIENT_MANIFEST.json": sha256_file(MANIFEST),
            "TRANSPORT_CONTRACT.json": sha256_file(TRANSPORT),
            "CANARIES.json": sha256_file(CANARIES),
            "verify_diag3_orbit5563_prover.py": sha256_file(Path(__file__)),
            "PROOF_NOTE.md": sha256_file(HERE / "PROOF_NOTE.md"),
        },
        "pinned_source_sha256": PINNED_SHA256,
        "covered_quantifiers": (
            "all 2604 realizable types, all 40320 frames per type, the entire "
            "hard-triple S8 torsor modulo the diagonal action, and all "
            "interior points for parent-sign, Cramer-chart, and factor-formula "
            "relabeling transport"
        ),
        "uncovered_quantifiers": (
            "all required closure strata and their residual-triple "
            "transition/attachment maps over every type and frame"
        ),
    }
    return seal(payload)


def validate_manifest(manifest: dict, exact: dict) -> None:
    if manifest.get("schema") != SCHEMA:
        raise GateError("manifest schema changed")
    group = manifest.get("group", {})
    if group.get("selected_stabilizer_order") != 1:
        raise GateError("hard presentation stabilizer claim changed")
    if group.get("selected_stabilizer") != [list(range(8))]:
        raise GateError("hard presentation stabilizer claim changed")
    quotient = manifest.get("quotient_definition", {})
    entries = manifest.get("catalog", {}).get("entries", [])
    quotient_classes = 0
    raw_multiplicity_sum = 0
    saw_nontrivial_parent_automorphism = False
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 3:
            raise GateError("parent automorphism reconciliation changed")
        _source_index, order, class_count = entry
        contribution = class_count * order
        if (
            order <= 0
            or GROUP_ORDER % order
            or class_count != GROUP_ORDER // order
        ):
            raise GateError("parent automorphism reconciliation changed")
        saw_nontrivial_parent_automorphism |= order > 1
        quotient_classes += class_count
        raw_multiplicity_sum += contribution
    if not saw_nontrivial_parent_automorphism:
        raise GateError("parent automorphism reconciliation changed")
    if quotient_classes != QUOTIENT_CLASSES:
        raise GateError("quotient class count changed")
    if raw_multiplicity_sum != RAW_GAUGE_REPRESENTATIVES:
        raise GateError("raw multiplicity sum changed")
    if quotient.get("number_of_quotient_classes") != quotient_classes:
        raise GateError("quotient class count changed")
    if quotient.get("sum_of_raw_multiplicities") != raw_multiplicity_sum:
        raise GateError("raw multiplicity sum changed")
    if manifest.get("semantic_sha256") != semantic_seal(manifest):
        raise GateError("manifest semantic seal changed")
    if manifest != exact:
        raise GateError("manifest differs from exact reconstruction")


def validate_transport(contract: dict, exact: dict) -> None:
    if contract.get("schema") != TRANSPORT_SCHEMA:
        raise GateError("transport schema changed")
    guards = contract.get("scope_guards", {})
    if guards.get("representative_matrix_covers_full_realization_space"):
        raise GateError("representative-matrix promotion prohibited")
    missing = contract.get("missing_transport", {})
    if missing.get("status") != "MISSING" and not missing.get(
        "attachment_artifacts"
    ):
        raise GateError("closure transport cannot pass without attachment artifacts")
    if guards.get("artificial_scope_boundary_is_true_parent_infinity"):
        raise GateError("artificial scope boundary is not true parent infinity")
    if guards.get("macrobox20_3468_attachment_accepted"):
        raise GateError("known false macrobox20 attachment cannot be accepted")
    if contract.get("terminal_classification") != "null":
        raise GateError("complete manifest with missing transport must be null")
    if guards.get("topology_computation_permitted_after_this_gate"):
        raise GateError("topology prohibited at terminal first-gate null")
    if contract.get("semantic_sha256") != semantic_seal(contract):
        raise GateError("transport semantic seal changed")
    if contract != exact:
        raise GateError("transport contract differs from exact reconstruction")


def validate_topology_claim(contract: dict, claim: str) -> None:
    if claim == "artificial_scope_boundary_as_infinity":
        raise GateError("artificial scope boundary is not true parent infinity")
    if not contract["scope_guards"]["topology_computation_permitted_after_this_gate"]:
        raise GateError("topology prohibited at terminal first-gate null")


def reseal(payload: dict) -> dict:
    payload["semantic_sha256"] = semantic_seal(payload)
    return payload


def expect_error(expected_text: str, operation) -> None:
    try:
        operation()
    except GateError as error:
        if expected_text not in str(error):
            raise GateError(
                f"wrong hostile-canary rejection: expected {expected_text!r}, "
                f"got {str(error)!r}"
            ) from error
    else:
        raise GateError(f"hostile canary unexpectedly accepted: {expected_text}")


def verify_canaries(
    stored: dict, manifest: dict, contract: dict, exact_manifest: dict,
    exact_contract: dict
) -> None:
    if stored != expected_canaries():
        raise GateError("canary fixture census changed")

    validate_manifest(manifest, exact_manifest)
    validate_transport(contract, exact_contract)

    dropped = copy.deepcopy(manifest)
    dropped["quotient_definition"]["sum_of_raw_multiplicities"] -= 1
    reseal(dropped)
    expect_error(
        "raw multiplicity sum changed",
        lambda: validate_manifest(dropped, exact_manifest),
    )

    collapsed = copy.deepcopy(manifest)
    nontrivial = next(
        entry
        for entry in collapsed["catalog"]["entries"]
        if entry[1] > 1
    )
    nontrivial[1] = 1
    reseal(collapsed)
    expect_error(
        "parent automorphism reconciliation changed",
        lambda: validate_manifest(collapsed, exact_manifest),
    )

    bad_stabilizer = copy.deepcopy(manifest)
    bad_stabilizer["group"]["selected_stabilizer_order"] = 2
    reseal(bad_stabilizer)
    expect_error(
        "hard presentation stabilizer claim changed",
        lambda: validate_manifest(bad_stabilizer, exact_manifest),
    )

    promoted = copy.deepcopy(contract)
    promoted["scope_guards"][
        "representative_matrix_covers_full_realization_space"
    ] = True
    reseal(promoted)
    expect_error(
        "representative-matrix promotion prohibited",
        lambda: validate_transport(promoted, exact_contract),
    )

    false_close = copy.deepcopy(contract)
    false_close["missing_transport"]["status"] = "PASS"
    reseal(false_close)
    expect_error(
        "closure transport cannot pass without attachment artifacts",
        lambda: validate_transport(false_close, exact_contract),
    )

    expect_error(
        "artificial scope boundary is not true parent infinity",
        lambda: validate_topology_claim(
            contract, "artificial_scope_boundary_as_infinity"
        ),
    )
    for claim in ("omitted_component", "unsound_edge", "positive_exit", "compact_component"):
        expect_error(
            "topology prohibited at terminal first-gate null",
            lambda claim=claim: validate_topology_claim(contract, claim),
        )

    prover_text = (ROOT / "ops/team/clipped-wall-prover/RESULT.yaml").read_text(
        encoding="utf-8"
    )
    falsifier_text = (
        ROOT / "ops/team/clipped-wall-falsifier/RESULT.yaml"
    ).read_text(encoding="utf-8")
    if (
        "outcome: disproved" not in prover_text
        or "proposed clipped-wall attachment is exactly impossible" not in prover_text
        or "outcome: disproved" not in falsifier_text
        or "proposed [3468] terminal attachment is impossible" not in falsifier_text
    ):
        raise GateError("pinned macrobox20 false-attachment canary changed")


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--emit", action="store_true", help="write the three deterministic artifacts"
    )
    args = parser.parse_args()

    verify_pinned_sources()
    exact_manifest = expected_manifest()
    exact_transport = expected_transport()
    exact_canaries = expected_canaries()

    if args.emit:
        write_json(MANIFEST, exact_manifest)
        write_json(TRANSPORT, exact_transport)
        write_json(CANARIES, exact_canaries)
        write_json(
            REPLAY,
            expected_replay_manifest(
                exact_manifest, exact_transport, exact_canaries
            ),
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = json.loads(TRANSPORT.read_text(encoding="utf-8"))
    canaries = json.loads(CANARIES.read_text(encoding="utf-8"))
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    validate_manifest(manifest, exact_manifest)
    validate_transport(contract, exact_transport)
    verify_canaries(
        canaries, manifest, contract, exact_manifest, exact_transport
    )
    exact_replay = expected_replay_manifest(manifest, contract, canaries)
    if replay != exact_replay or replay.get("semantic_sha256") != semantic_seal(
        replay
    ):
        raise GateError("replay verification manifest changed")

    print(
        "PASS exact quotient manifest: "
        "100086840 classes; raw multiplicities sum to 104993280"
    )
    print(
        "PASS parent automorphism/Burnside histogram: "
        "1:2382 2:183 3:10 4:16 6:3 8:6 12:1 16:1 24:2"
    )
    print("PASS hard presentation stabilizer=identity and orbit=40320")
    print("PASS diagonal gauge slice is free, exhaustive, and unique")
    print("MANIFEST_SEMANTIC_SHA256", manifest["semantic_sha256"])
    print("PASS interior signs/charts/factor relabeling for all points and frames")
    print(
        "NULL missing all-parent closure-stratum transport and attachment atlas"
    )
    print("TRANSPORT_SEMANTIC_SHA256", contract["semantic_sha256"])
    print("PASS 13/13 positive, null, negative, and hostile canaries")
    print("REPLAY_MANIFEST_SHA256", sha256_file(REPLAY))
    print("STOP no topology computation; row=1162302 ledger change=none pivot=required")


if __name__ == "__main__":
    main()
