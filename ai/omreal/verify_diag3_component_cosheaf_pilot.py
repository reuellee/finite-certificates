#!/usr/bin/env python3
"""Independent verifier for the bounded component/cosheaf strategy pilot.

This verifier never imports the pilot producer.  It authenticates four
existing master-closure fixtures with their accepted source replayers,
recomputes the component diagram and exact mod-two homology, and checks the
large two-support inputs directly.  Fourteen re-sealed hostile mutations exercise
the fail-closed decision contract.
"""

from __future__ import annotations

from collections import Counter
import copy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CERTIFICATE = DATA / "DIAG3_COMPONENT_COSHEAF_PILOT.json"

CANARIES = {
    "schema_relative": DATA / "DIAG3_PAIR_MASTER_CLOSURE_V1_CANARY.json",
    "transverse_node": DATA / "DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.json",
    "multibox": DATA / "DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.json",
    "first_event": DATA / "DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.json",
}

TWO_SUPPORT_INPUTS = {
    "gate": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json",
    "base": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.json",
    "open_t_open_u": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json",
    "open_t_algebraic_u": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json",
    "algebraic_t_open_u": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json",
    "algebraic_t_regular_u": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json",
    "algebraic_t_final_u": DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json",
}

REQUIRED_FIELDS = (
    "cells",
    "strict_closure_pairs",
    "strict_three_cell_chains",
    "parent_infinity_subcomplex",
    "signature_profile_source",
)

sys.path.insert(0, str(HERE))
import verify_diag3_pair_master_closure_multibox_canary as multibox_verifier  # noqa: E402
import verify_diag3_pair_master_closure_node_canary as node_verifier  # noqa: E402
import verify_diag3_pair_master_closure_certificate_v1 as schema_verifier  # noqa: E402
import verify_diag3_pair_master_closure_first_event as first_event_verifier  # noqa: E402
import diag3_pair_first_event_core as first_event_core  # noqa: E402


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_digest(payload) -> str:
    core = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    return sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def rank_f2_by_columns(matrix) -> int:
    if not matrix:
        return 0
    row_count = len(matrix)
    column_count = len(matrix[0])
    columns = [
        sum((int(matrix[row][column]) & 1) << row for row in range(row_count))
        for column in range(column_count)
    ]
    pivots = {}
    for word in columns:
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    return len(pivots)


def signed_boundary(record, lower, upper, key):
    lower_position = {identifier: index for index, identifier in enumerate(lower)}
    upper_position = {identifier: index for index, identifier in enumerate(upper)}
    matrix = [[0 for _ in upper] for _ in lower]
    for low, high, coefficient in record["integral_boundary"][key]:
        if low in lower_position and high in upper_position:
            matrix[lower_position[low]][upper_position[high]] += int(coefficient)
    return matrix


def verify_zero_product(d1, d2):
    for row in range(len(d1)):
        for column in range(len(d2[0]) if d2 else 0):
            require(
                sum(d1[row][middle] * d2[middle][column] for middle in range(len(d2))) == 0,
                "restricted signed boundary has nonzero square",
            )


def component_records(cell_map, selected):
    vertices = sorted(
        identifier for identifier in selected if cell_map[identifier]["dimension"] == 0
    )
    parent = {identifier: identifier for identifier in vertices}

    def find(identifier):
        while parent[identifier] != identifier:
            parent[identifier] = parent[parent[identifier]]
            identifier = parent[identifier]
        return identifier

    def union(left, right):
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for identifier in selected:
        cell = cell_map[identifier]
        if cell["dimension"] == 1:
            endpoints = [face for face in cell["boundary"] if face in parent]
            require(len(endpoints) == 2, f"edge endpoint count {identifier}")
            union(*endpoints)

    groups = {}
    for vertex in vertices:
        groups.setdefault(find(vertex), set()).add(vertex)

    def closure_vertices(identifier):
        pending = [identifier]
        answer = set()
        while pending:
            current = pending.pop()
            if cell_map[current]["dimension"] == 0:
                answer.add(current)
            else:
                pending.extend(cell_map[current]["boundary"])
        return answer

    result = []
    for vertices_in_component in sorted(groups.values(), key=lambda item: min(item)):
        incident = [
            identifier for identifier in selected
            if closure_vertices(identifier) & vertices_in_component
        ]
        result.append({
            "id": min(vertices_in_component),
            "vertices": sorted(vertices_in_component),
            "incident_cell_count": len(incident),
        })
    return result


def intersection_summary(record, selected):
    cell_map = {cell["id"]: cell for cell in record["cells"]}
    basis = {
        dimension: sorted(
            identifier for identifier in selected
            if cell_map[identifier]["dimension"] == dimension
        )
        for dimension in range(3)
    }
    d1 = signed_boundary(record, basis[0], basis[1], "d1_entries")
    d2 = signed_boundary(record, basis[1], basis[2], "d2_entries")
    verify_zero_product(d1, d2)
    rank1 = rank_f2_by_columns(d1)
    rank2 = rank_f2_by_columns(d2)
    components = component_records(cell_map, selected)
    b0 = len(basis[0]) - rank1
    require(b0 == len(components), "graph components disagree with cellular H0")
    return {
        "cell_census": {str(dimension): len(basis[dimension]) for dimension in range(3)},
        "component_count": len(components),
        "components": components,
        "b0_f2": b0,
        "b1_f2": len(basis[1]) - rank1 - rank2,
        "rank_boundary_1_f2": rank1,
        "rank_boundary_2_f2": rank2,
    }


def component_containing(summary, vertices):
    targets = {
        component["id"] for vertex in vertices for component in summary["components"]
        if vertex in component["vertices"]
    }
    require(len(targets) == 1, "component specialization split inside its target")
    return next(iter(targets))


def histogram_rows(histogram):
    return [
        {"result": list(result), "ordered_profile_triples": count}
        for result, count in sorted(histogram.items())
    ]


def schema_rank_histogram(record, profile_bad):
    cell_map = {cell["id"]: cell for cell in record["cells"]}
    vertices = sorted(
        identifier for identifier, cell in cell_map.items() if cell["dimension"] == 0
    )
    index = {identifier: position for position, identifier in enumerate(vertices)}
    closure = {tuple(row) for row in record["strict_closure_pairs"]}
    cell_simplex = {}
    for identifier, cell in cell_map.items():
        closure_vertices = [
            vertex for vertex in vertices
            if identifier == vertex or (identifier, vertex) in closure
        ]
        require(
            len(closure_vertices) == cell["dimension"] + 1,
            "schema fixture is not native simplicial",
        )
        cell_simplex[identifier] = tuple(sorted(index[vertex] for vertex in closure_vertices))
    maximal = tuple(
        cell_simplex[identifier] for identifier, cell in cell_map.items()
        if cell["dimension"] == 2
    )
    infinity = frozenset(
        cell_simplex[identifier] for identifier in record["parent_infinity_subcomplex"]
    )
    complex_ = node_verifier.master.MasterComplex(maximal, infinity)
    bad = {
        profile: {cell_simplex[identifier] for identifier in identifiers}
        for profile, identifiers in profile_bad.items()
    }
    histogram = Counter()
    for triple in product(sorted(profile_bad), repeat=3):
        result = complex_.extract(tuple(bad[profile] for profile in triple)).result()
        require(result[-1] == 0, "schema relative middle residue")
        histogram[result] += 1
    return histogram


def expected_canary(name, path, verifier=None):
    record = read_json(path)
    if "signature_profile_source" in record:
        profiles = record["signature_profile_source"]["profiles"]
        bad_by_mask = {
            int(profile["feasible_chamber_mask"]): set(profile["bad_cells"])
            for profile in profiles
        }
        profile_source = "complete_extension_signature_profiles"
    else:
        bad_by_mask = {
            signature: set(identifiers)
            for signature, identifiers in record["bad_signature_membership"].items()
        }
        profiles = list(bad_by_mask)
        profile_source = "schema_canary_bad_signature_membership"

    if name == "schema_relative":
        schema_verifier.validate(record)
        histogram = schema_rank_histogram(record, bad_by_mask)
    elif name == "first_event":
        replay = first_event_verifier.validate(record, first_event_core.build_record())
        histogram = Counter({
            (
                int(row["dim_c1"]),
                int(row["rank_n"]),
                int(row["rank_m"]),
                int(row["dim_h1"]),
            ): int(row["profile_triple_count"])
            for row in replay["rank_histogram"]
        })
    else:
        histogram = verifier.validate(record, verifier.replay_sources())
    closure = {tuple(row) for row in record["strict_closure_pairs"]}
    for mask, bad in bad_by_mask.items():
        require(
            all(low in bad for high, low in closure if high in bad),
            f"profile {mask} is not closed",
        )

    intersections = {}
    masks = sorted(bad_by_mask)
    for size in range(1, 4):
        for chosen in combinations(masks, size):
            selected = set.intersection(*(bad_by_mask[mask] for mask in chosen))
            intersections[",".join(map(str, chosen))] = intersection_summary(record, selected)

    maps = []
    for size in (2, 3):
        for chosen in combinations(masks, size):
            child_key = ",".join(map(str, chosen))
            child = intersections[child_key]
            for omitted in range(size):
                parent_tuple = chosen[:omitted] + chosen[omitted + 1 :]
                parent_key = ",".join(map(str, parent_tuple))
                parent_summary = intersections[parent_key]
                mapping = [
                    [component["id"], component_containing(parent_summary, component["vertices"])]
                    for component in child["components"]
                ]
                maps.append({
                    "source": child_key,
                    "target": parent_key,
                    "component_map": mapping,
                })

    rows = histogram_rows(histogram)
    return {
        "source_sha256": file_sha256(path),
        "source_format": record["format"],
        "master_cell_count": len(record["cells"]),
        "strict_closure_pair_count": len(record["strict_closure_pairs"]),
        "strict_three_cell_chain_count": len(record["strict_three_cell_chains"]),
        "profile_count": len(profiles),
        "profile_source": profile_source,
        "simplicialization": (
            "native_triangular_regular_cw"
            if name in {"schema_relative", "transverse_node"}
            else "barycentric_order_complex"
        ),
        "rank_replay_source": (
            "authenticated_source_rank_replay_with_integral_exactness_lift"
            if name == "first_event"
            else "recomputed_from_signed_integral_complex"
        ),
        "ordered_profile_triple_count": sum(histogram.values()),
        "profile_intersections_through_order_three": intersections,
        "component_specialization_maps": maps,
        "maximum_intersection_component_count": max(
            summary["component_count"] for summary in intersections.values()
        ),
        "nontrivial_split_merge_exercised": any(
            summary["component_count"] > 1 for summary in intersections.values()
        ),
        "balanced_pair_rank_histogram_f2": rows,
        # The authenticated canary extractor proves d^2=0 and rank_Q >= rank_F2
        # termwise.  Since every F2 residue is zero, rank_Q cannot increase in
        # either differential; hence the rational histogram is identical.
        "balanced_pair_rank_histogram_q": rows,
        "all_ordered_profile_triples_middle_exact_f2": True,
        "all_ordered_profile_triples_middle_exact_q": True,
        "scope_boundary_retained_as_ordinary": bool(record.get("scope_boundary_subcomplex")),
        "parent_infinity_cell_count": len(record["parent_infinity_subcomplex"]),
        "parent_infinity_interpretation": (
            "declared_schema_relative_interface_only"
            if record.get("status") == "SCHEMA_CANARY"
            else "empty_local_fixture_declaration"
        ),
    }


def expected_two_support_audit():
    records = {name: read_json(path) for name, path in TWO_SUPPORT_INPUTS.items()}
    gate = records["gate"]
    open_cells = records["open_t_open_u"]["open_cell_v_lift"]
    open_sections = records["open_t_algebraic_u"]["cumulative_open_t_algebraic_u_section_v_lift"]
    algebraic = records["algebraic_t_final_u"]["cumulative_algebraic_t_v_lift"]
    missing = {
        name: [field for field in REQUIRED_FIELDS if field not in record]
        for name, record in records.items()
    }
    base_partition = {
        "open_t_open_u": int(open_cells["open_base_cells"]),
        "open_t_algebraic_u": int(open_sections["completed_sections"]),
        "algebraic_t": int(algebraic["base_cells"]),
    }
    base_partition["total"] = sum(base_partition.values())
    lift_partition = {
        "open_t_open_u": int(open_cells["lifted_cells"]),
        "open_t_algebraic_u": int(open_sections["lifted_cells"]),
        "algebraic_t": int(algebraic["lifted_cells"]),
    }
    lift_partition["total"] = sum(lift_partition.values())
    return {
        "source_sha256": {name: file_sha256(path) for name, path in TWO_SUPPORT_INPUTS.items()},
        "covered_parent_supports": [domain["support"] for domain in gate["parent_domains"]],
        "base_cell_partition": base_partition,
        "lifted_cell_partition": lift_partition,
        "missing_required_fields_by_artifact": missing,
        "all_inputs_missing_at_least_one_required_field": all(missing.values()),
        "fiber_signature_semantics": "ordered residual-wall roots and event attachments; not extension-signature bad-membership profiles",
        "global_gluing_claims": {
            name: record.get("scope", {}).get("global_gluing_and_closure_data", "FIELD_ABSENT")
            for name, record in records.items()
        },
        "compiler_result": "FAIL_CLOSED_BEFORE_COMPONENT_SPECIALIZATION",
        "blocking_contract": [
            "face-compatible regular-cell identifiers across every adjacent t/u/v stratum",
            "complete strict closure pairs and strict three-cell chains",
            "true parent-infinity membership rather than local-scope boundary tags",
            "complete extension-signature bad-membership profiles on every retained stratum",
        ],
    }


def expected_payload_parts():
    canary_replay = {
            "schema_relative": expected_canary(
                "schema_relative", CANARIES["schema_relative"]
            ),
            "transverse_node": expected_canary(
                "transverse_node", CANARIES["transverse_node"], node_verifier
            ),
            "multibox": expected_canary(
                "multibox", CANARIES["multibox"], multibox_verifier
            ),
            "first_event": expected_canary(
                "first_event", CANARIES["first_event"]
            ),
        }
    intersections = [
        summary
        for fixture in canary_replay.values()
        for summary in fixture["profile_intersections_through_order_three"].values()
    ]
    maps = [
        mapping
        for fixture in canary_replay.values()
        for mapping in fixture["component_specialization_maps"]
    ]
    return {
        "canary_replay": canary_replay,
        "fixture_limit_census": {
            "distinct_profile_intersections": len(intersections),
            "component_specialization_maps": len(maps),
            "disconnected_intersections": sum(
                summary["component_count"] > 1 for summary in intersections
            ),
            "many_to_one_component_maps": sum(
                len(mapping["component_map"]) > len({target for _, target in mapping["component_map"]})
                for mapping in maps
            ),
            "nonzero_b1_intersections": sum(summary["b1_f2"] > 0 for summary in intersections),
            "nonzero_d2_rank_intersections": sum(
                summary["rank_boundary_2_f2"] > 0 for summary in intersections
            ),
            "maximum_d2_rank_f2": max(
                summary["rank_boundary_2_f2"] for summary in intersections
            ),
            "nonempty_declared_parent_infinity_fixtures": sum(
                fixture["parent_infinity_cell_count"] > 0 for fixture in canary_replay.values()
            ),
        },
        "two_support_input_audit": expected_two_support_audit(),
    }


def validate(record, expected):
    require(set(record) == {
        "format", "status", "scope", "method_contract", "canary_replay",
        "fixture_limit_census",
        "two_support_input_audit", "decision", "citations", "verifier",
        "semantic_sha256",
    }, "top-level fields")
    require(record["format"] == "diag3-component-cosheaf-strategy-pilot-v1", "format")
    require(record["status"] == "BOUNDED_NO_GO", "status")
    require(record["semantic_sha256"] == semantic_digest(record), "semantic digest")
    require(record["scope"] == {
        "parent_index": 2599,
        "pilot_supports": [[3, 1, 15], [3, 3, 7]],
        "honest_9dvl_score": "2/9",
        "pair_branch_closed": False,
        "triple_branch_closed": False,
    }, "scope")
    require(record["method_contract"] == {
        "roadmap_role": "certify connected-component incidence only",
        "first_betti_role": "retain overlap, two-cell, and signed frontier data; a graph alone is insufficient",
        "cosheaf_role": "compress only after a certified face poset and specialization maps exist",
        "split_merge_role": "promotion requires a fixture with a nontrivial component split or merge",
        "infinity_role": "use the genuine parent-infinity subcomplex in the relative complex",
        "morse_role": "post-certificate compression only",
    }, "method contract")
    require(record["canary_replay"] == expected["canary_replay"], "canary component/rank replay")
    require(record["fixture_limit_census"] == expected["fixture_limit_census"], "fixture limitation census")
    require(
        record["two_support_input_audit"] == expected["two_support_input_audit"],
        "two-support input contract audit",
    )
    require(record["decision"] == {
        "promote_existing_manifests_as_master_closure_replacement": False,
        "result": "BOUNDED_NO_GO",
        "no_go_scope": "reuse completed two-support lift manifests as global component-cosheaf input without new closure construction",
        "boundary_aware_roadmap_method": "OPEN_EXPERIMENT_NOT_TESTED_ON_EITHER_SUPPORT",
        "reason": "the completed fiber inventories do not encode closure-complete component specialization, complete bad-signature labels, or true-infinity incidence",
        "safe_reuse": "use component/cosheaf reduction after the master closure compiler emits the missing incidence contract",
        "next_pair_action": "compile exact face-compatible closure and signature labels across the completed two-support fibers, beginning with the section-960 collision and section-550 endpoint-tangency stars",
        "next_triple_action": "retain the independently selected boundary-complete projection-critical roadmap route",
    }, "decision")
    require(record["citations"] == [
        "Basu-Pollack-Roy arXiv:math/0603248",
        "Basu-Roy Divide and Conquer Roadmap for Algebraic Sets",
        "Kishimoto-Yushima arXiv:2202.03659",
        "Forman, Morse Theory for Cell Complexes, Adv. Math. 134 (1998)",
    ], "citation pins")
    require(record["verifier"] == {
        "command": "python ai/omreal/verify_diag3_component_cosheaf_pilot.py",
        "hostile_mutations_required": 14,
    }, "verifier contract")


def reseal(record):
    record["semantic_sha256"] = semantic_digest(record)
    return record


def assert_rejected(record, expected, label):
    try:
        validate(reseal(record), expected)
    except (CertificateError, KeyError, IndexError, TypeError, ValueError):
        return
    raise AssertionError(f"hostile mutation accepted: {label}")


def main():
    record = read_json(CERTIFICATE)
    expected = expected_payload_parts()
    validate(record, expected)

    mutations = []
    corrupt = copy.deepcopy(record); corrupt["status"] = "PROVED"; mutations.append((corrupt, "promoted status"))
    corrupt = copy.deepcopy(record); corrupt["scope"]["honest_9dvl_score"] = "3/9"; mutations.append((corrupt, "inflated ledger"))
    corrupt = copy.deepcopy(record); corrupt["scope"]["pair_branch_closed"] = True; mutations.append((corrupt, "false pair closure"))
    corrupt = copy.deepcopy(record); corrupt["scope"]["triple_branch_closed"] = True; mutations.append((corrupt, "false triple closure"))
    corrupt = copy.deepcopy(record); corrupt["decision"]["promote_existing_manifests_as_master_closure_replacement"] = True; mutations.append((corrupt, "false promotion"))
    corrupt = copy.deepcopy(record); corrupt["two_support_input_audit"]["compiler_result"] = "PASS"; mutations.append((corrupt, "missing compiler inputs ignored"))
    corrupt = copy.deepcopy(record); corrupt["two_support_input_audit"]["lifted_cell_partition"]["total"] -= 1; mutations.append((corrupt, "lift count"))
    corrupt = copy.deepcopy(record); corrupt["two_support_input_audit"]["missing_required_fields_by_artifact"]["open_t_open_u"].pop(); mutations.append((corrupt, "missing field suppressed"))
    corrupt = copy.deepcopy(record); corrupt["two_support_input_audit"]["source_sha256"]["gate"] = "0" * 64; mutations.append((corrupt, "source hash"))
    corrupt = copy.deepcopy(record); corrupt["canary_replay"]["transverse_node"]["profile_intersections_through_order_three"]["0"]["b1_f2"] += 1; mutations.append((corrupt, "canary Betti number"))
    corrupt = copy.deepcopy(record); corrupt["canary_replay"]["schema_relative"]["parent_infinity_cell_count"] = 0; mutations.append((corrupt, "true infinity erased"))
    corrupt = copy.deepcopy(record); corrupt["canary_replay"]["first_event"]["component_specialization_maps"][0]["target"] = "corrupt"; mutations.append((corrupt, "specialization map"))
    corrupt = copy.deepcopy(record); corrupt["canary_replay"]["first_event"]["balanced_pair_rank_histogram_f2"][0]["ordered_profile_triples"] += 1; mutations.append((corrupt, "pair-rank histogram"))
    corrupt = copy.deepcopy(record); corrupt["canary_replay"]["first_event"]["nontrivial_split_merge_exercised"] = True; mutations.append((corrupt, "invented split-merge coverage"))
    require(len(mutations) == 14, "hostile mutation census")
    for corrupt, label in mutations:
        assert_rejected(corrupt, expected, label)

    audit = record["two_support_input_audit"]
    print("PASS independently authenticated schema, node, multibox, and first-event complexes")
    print("PASS component records, specialization maps, signed d^2=0, and F2 H0/H1 replayed")
    print("PASS declared relative-infinity schema interface and 8+216+216+512 ordered pair-rank replays")
    print("PASS exact two-support inventory", audit["base_cell_partition"]["total"], audit["lifted_cell_partition"]["total"])
    print("PASS fail-closed compiler contract: closure, labels, infinity, and incidence are absent")
    print("PASS 14/14 re-sealed hostile mutations rejected")
    print("STATUS BOUNDED_NO_GO; honest 9DVL score remains 2/9")


if __name__ == "__main__":
    main()
