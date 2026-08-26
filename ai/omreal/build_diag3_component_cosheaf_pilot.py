#!/usr/bin/env python3
"""Build the bounded diagonal-three component/cosheaf strategy pilot.

The producer deliberately has two roles only:

* compress four fixed master fixtures (including a synthetic
  relative-infinity schema fixture and the 399-cell first-event atlas) to
  component and first-Betti records; and
* audit whether the completed first-two-four-support lift artifacts expose the
  fields needed to run the same compiler.

It does not infer closure, extension-signature labels, or infinity from the
large lift counts.  Missing proof data therefore produce an input-contract
``BOUNDED_NO_GO`` for reusing the completed lift manifests as-is.  This does
not assert that a new boundary-aware roadmap could not produce the missing
data efficiently.
"""

from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_COMPONENT_COSHEAF_PILOT.json"

FORMAT = "diag3-component-cosheaf-strategy-pilot-v1"
STATUS = "BOUNDED_NO_GO"

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

REQUIRED_COMPILER_FIELDS = (
    "cells",
    "strict_closure_pairs",
    "strict_three_cell_chains",
    "parent_infinity_subcomplex",
    "signature_profile_source",
)

def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rank_f2(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    columns = len(matrix[0])
    words = [
        sum((int(value) & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    pivot = 0
    for column in range(columns):
        selected = next(
            (row for row in range(pivot, len(words)) if words[row] >> column & 1),
            None,
        )
        if selected is None:
            continue
        words[pivot], words[selected] = words[selected], words[pivot]
        for row in range(len(words)):
            if row != pivot and words[row] >> column & 1:
                words[row] ^= words[pivot]
        pivot += 1
        if pivot == len(words):
            break
    return pivot


def rank_q(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    work = [[Fraction(value) for value in row] for row in matrix]
    columns = len(work[0])
    pivot = 0
    for column in range(columns):
        selected = next(
            (row for row in range(pivot, len(work)) if work[row][column]), None
        )
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [value / scale for value in work[pivot]]
        for row in range(len(work)):
            if row == pivot or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * basis
                for value, basis in zip(work[row], work[pivot])
            ]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def boundary_matrix(lower: list[str], upper: list[str], entries) -> list[list[int]]:
    lower_index = {identifier: index for index, identifier in enumerate(lower)}
    upper_index = {identifier: index for index, identifier in enumerate(upper)}
    matrix = [[0 for _ in upper] for _ in lower]
    for low, high, coefficient in entries:
        if low in lower_index and high in upper_index:
            matrix[lower_index[low]][upper_index[high]] += int(coefficient)
    return matrix


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left:
        return []
    inner = len(left[0])
    if inner == 0:
        return [[0 for _ in range(len(right[0]) if right else 0)] for _ in left]
    columns = len(right[0]) if right else 0
    return [
        [sum(left[row][mid] * right[mid][column] for mid in range(inner)) for column in range(columns)]
        for row in range(len(left))
    ]


def simplicial_incidence(lower, upper) -> list[list[int]]:
    positions = {cell: index for index, cell in enumerate(lower)}
    matrix = [[0 for _ in lower] for _ in upper]
    for row, cell in enumerate(upper):
        for omitted in range(len(cell)):
            face = cell[:omitted] + cell[omitted + 1 :]
            column = positions.get(face)
            if column is not None:
                matrix[row][column] += -1 if omitted & 1 else 1
    return matrix


def block_matrix(row_dimensions, column_dimensions, blocks) -> list[list[int]]:
    row_offsets = [0]
    column_offsets = [0]
    for dimension in row_dimensions:
        row_offsets.append(row_offsets[-1] + dimension)
    for dimension in column_dimensions:
        column_offsets.append(column_offsets[-1] + dimension)
    answer = [
        [0 for _ in range(column_offsets[-1])] for _ in range(row_offsets[-1])
    ]
    for (block_row, block_column), (coefficient, matrix) in blocks.items():
        if len(matrix) != row_dimensions[block_row]:
            raise AssertionError("block row dimension")
        if matrix and len(matrix[0]) != column_dimensions[block_column]:
            raise AssertionError("block column dimension")
        for row, values in enumerate(matrix):
            for column, value in enumerate(values):
                answer[row_offsets[block_row] + row][
                    column_offsets[block_column] + column
                ] = coefficient * value
    return answer


def barycentric_cells(record):
    identifiers = sorted(
        (cell["id"] for cell in record["cells"]),
        key=lambda identifier: (
            next(cell["dimension"] for cell in record["cells"] if cell["id"] == identifier),
            identifier,
        ),
    )
    index = {identifier: position for position, identifier in enumerate(identifiers)}
    cells = {(index[identifier],) for identifier in identifiers}
    cells.update(
        tuple(sorted((index[high], index[low])))
        for high, low in record["strict_closure_pairs"]
    )
    cells.update(
        tuple(sorted((index[high], index[middle], index[low])))
        for high, middle, low in record["strict_three_cell_chains"]
    )
    return tuple(sorted(cells, key=lambda cell: (len(cell), cell))), index


def simplicial_model(record, bad_by_mask):
    if record["format"] == "diag3-pair-master-closure-certificate-v1":
        cell_map = {cell["id"]: cell for cell in record["cells"]}
        vertices = sorted(
            identifier for identifier, cell in cell_map.items()
            if cell["dimension"] == 0
        )
        index = {identifier: position for position, identifier in enumerate(vertices)}
        closure_pairs = {tuple(row) for row in record["strict_closure_pairs"]}
        cell_to_simplex = {}
        for identifier, cell in cell_map.items():
            closure_vertices = [
                vertex for vertex in vertices
                if identifier == vertex or (identifier, vertex) in closure_pairs
            ]
            if len(closure_vertices) != cell["dimension"] + 1:
                raise AssertionError("native canary cell is not a simplex")
            cell_to_simplex[identifier] = tuple(
                sorted(index[vertex] for vertex in closure_vertices)
            )
        cells = tuple(
            sorted(set(cell_to_simplex.values()), key=lambda cell: (len(cell), cell))
        )
        bad_sets = {
            mask: {cell_to_simplex[identifier] for identifier in bad}
            for mask, bad in bad_by_mask.items()
        }
        relative = {
            cell_to_simplex[identifier]
            for identifier in record["parent_infinity_subcomplex"]
        }
        return cells, bad_sets, relative, "native_triangular_regular_cw"

    cells, index = barycentric_cells(record)
    bad_sets = {}
    for mask, bad in bad_by_mask.items():
        bad_vertices = {index[identifier] for identifier in bad}
        bad_sets[mask] = {cell for cell in cells if set(cell) <= bad_vertices}
    infinity_vertices = {
        index[identifier] for identifier in record["parent_infinity_subcomplex"]
    }
    relative = {cell for cell in cells if set(cell) <= infinity_vertices}
    return cells, bad_sets, relative, "barycentric_order_complex"


def pair_rank(cells, bad_by_mask, relative, profile_triple):
    bad_sets = [bad_by_mask[mask] for mask in profile_triple]
    triple = set.intersection(*bad_sets)
    pairs = ((0, 1), (0, 2), (1, 2))
    exclusive = [
        (bad_sets[left] & bad_sets[right]) - triple for left, right in pairs
    ]

    def basis(source, degree):
        return tuple(
            cell for cell in cells
            if len(cell) == degree + 1 and cell in source and cell not in relative
        )

    triple_basis = tuple(basis(triple, degree) for degree in range(3))
    exclusive_basis = tuple(
        tuple(basis(source, degree) for degree in range(3)) for source in exclusive
    )
    d_triple = (
        simplicial_incidence(triple_basis[0], triple_basis[1]),
        simplicial_incidence(triple_basis[1], triple_basis[2]),
    )
    if any(value for row in multiply(d_triple[1], d_triple[0]) for value in row):
        raise AssertionError("triple coboundary does not square to zero")

    differentials = []
    frontiers = []
    for strata_basis in exclusive_basis:
        differential = (
            simplicial_incidence(strata_basis[0], strata_basis[1]),
            simplicial_incidence(strata_basis[1], strata_basis[2]),
        )
        frontier = (
            simplicial_incidence(triple_basis[0], strata_basis[1]),
            simplicial_incidence(triple_basis[1], strata_basis[2]),
        )
        if any(value for row in multiply(differential[1], differential[0]) for value in row):
            raise AssertionError("exclusive-pair coboundary does not square to zero")
        differentials.append(differential)
        frontiers.append(frontier)

    triple_dimensions = tuple(len(row) for row in triple_basis)
    exclusive_dimensions = tuple(
        tuple(len(row) for row in strata_basis) for strata_basis in exclusive_basis
    )
    c0_dimensions = (triple_dimensions[0], triple_dimensions[0]) + tuple(
        dimensions[0] for dimensions in exclusive_dimensions
    )
    c1_dimensions = (triple_dimensions[1], triple_dimensions[1]) + tuple(
        dimensions[1] for dimensions in exclusive_dimensions
    )
    c2_dimensions = (triple_dimensions[2], triple_dimensions[2]) + tuple(
        dimensions[2] for dimensions in exclusive_dimensions
    )
    n_matrix = block_matrix(
        c1_dimensions,
        c0_dimensions,
        {
            (0, 0): (1, d_triple[0]),
            (1, 1): (1, d_triple[0]),
            (2, 0): (-1, frontiers[0][0]),
            (2, 2): (1, differentials[0][0]),
            (3, 0): (-1, frontiers[1][0]),
            (3, 1): (-1, frontiers[1][0]),
            (3, 3): (1, differentials[1][0]),
            (4, 1): (-1, frontiers[2][0]),
            (4, 4): (1, differentials[2][0]),
        },
    )
    m_matrix = block_matrix(
        c2_dimensions,
        c1_dimensions,
        {
            (0, 0): (1, d_triple[1]),
            (1, 1): (1, d_triple[1]),
            (2, 0): (1, frontiers[0][1]),
            (2, 2): (-1, differentials[0][1]),
            (3, 0): (1, frontiers[1][1]),
            (3, 1): (1, frontiers[1][1]),
            (3, 3): (-1, differentials[1][1]),
            (4, 1): (1, frontiers[2][1]),
            (4, 4): (-1, differentials[2][1]),
        },
    )
    if any(value for row in multiply(m_matrix, n_matrix) for value in row):
        raise AssertionError("assembled signed integral matrices have nonzero product")
    middle = len(n_matrix)
    rank_n_f2 = rank_f2(n_matrix)
    rank_m_f2 = rank_f2(m_matrix)
    rank_n_q = rank_q(n_matrix)
    rank_m_q = rank_q(m_matrix)
    return (
        (middle, rank_n_f2, rank_m_f2, middle - rank_n_f2 - rank_m_f2),
        (middle, rank_n_q, rank_m_q, middle - rank_n_q - rank_m_q),
    )


def components(cell_map, selected: set[str]) -> list[dict]:
    vertices = sorted(
        identifier for identifier in selected if cell_map[identifier]["dimension"] == 0
    )
    adjacency = {vertex: set() for vertex in vertices}
    for identifier in selected:
        cell = cell_map[identifier]
        if cell["dimension"] != 1:
            continue
        ends = [face for face in cell["boundary"] if face in adjacency]
        if len(ends) == 2:
            adjacency[ends[0]].add(ends[1])
            adjacency[ends[1]].add(ends[0])
    answer = []
    unseen = set(vertices)
    while unseen:
        start = min(unseen)
        queue = deque([start])
        reached = {start}
        unseen.remove(start)
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    reached.add(neighbor)
                    queue.append(neighbor)
        def closure_vertices(identifier):
            frontier = [identifier]
            answer = set()
            while frontier:
                current = frontier.pop()
                if cell_map[current]["dimension"] == 0:
                    answer.add(current)
                else:
                    frontier.extend(cell_map[current].get("boundary", ()))
            return answer

        incident_cells = sorted(
            identifier for identifier in selected
            if closure_vertices(identifier).intersection(reached)
        )
        answer.append({
            "id": start,
            "vertices": sorted(reached),
            "incident_cell_count": len(incident_cells),
        })
    return answer


def subcomplex_summary(record, selected: set[str]) -> dict:
    cell_map = {cell["id"]: cell for cell in record["cells"]}
    census = Counter(cell_map[identifier]["dimension"] for identifier in selected)
    basis = {
        dimension: sorted(
            identifier for identifier in selected
            if cell_map[identifier]["dimension"] == dimension
        )
        for dimension in range(3)
    }
    boundary = record["integral_boundary"]
    d1 = boundary_matrix(basis[0], basis[1], boundary["d1_entries"])
    d2 = boundary_matrix(basis[1], basis[2], boundary["d2_entries"])
    product = multiply(d1, d2)
    if any(value for row in product for value in row):
        raise AssertionError("restricted integral boundary does not square to zero")
    rank1 = rank_f2(d1)
    rank2 = rank_f2(d2)
    component_records = components(cell_map, selected)
    b0 = len(basis[0]) - rank1
    b1 = len(basis[1]) - rank1 - rank2
    if b0 != len(component_records):
        raise AssertionError("component graph and cellular H0 disagree")
    return {
        "cell_census": {str(dimension): census.get(dimension, 0) for dimension in range(3)},
        "component_count": len(component_records),
        "components": component_records,
        "b0_f2": b0,
        "b1_f2": b1,
        "rank_boundary_1_f2": rank1,
        "rank_boundary_2_f2": rank2,
    }


def component_target(summary: dict, vertex: str) -> str:
    for component in summary["components"]:
        if vertex in component["vertices"]:
            return component["id"]
    raise AssertionError(f"component vertex {vertex} has no target")


def canary_component_cosheaf(path: Path) -> dict:
    record = read_json(path)
    cell_map = {cell["id"]: cell for cell in record["cells"]}
    if "signature_profile_source" in record:
        profiles = record["signature_profile_source"]["profiles"]
        profile_bad = {
            int(profile["feasible_chamber_mask"]): set(profile["bad_cells"])
            for profile in profiles
        }
        profile_source = "complete_extension_signature_profiles"
    else:
        profile_bad = {
            signature: set(bad)
            for signature, bad in record["bad_signature_membership"].items()
        }
        profiles = list(profile_bad)
        profile_source = "schema_canary_bad_signature_membership"
    for bad in profile_bad.values():
        for identifier in bad:
            if not set(cell_map[identifier]["boundary"]).issubset(bad):
                raise AssertionError("bad-cell profile is not closed")

    simplices, simplicial_bad, simplicial_infinity, simplicialization = simplicial_model(
        record, profile_bad
    )
    if "rank_replay" in record:
        f2_histogram = Counter({
            (
                int(row["dim_c1"]),
                int(row["rank_n"]),
                int(row["rank_m"]),
                int(row["dim_h1"]),
            ): int(row["profile_triple_count"])
            for row in record["rank_replay"]["rank_histogram"]
        })
        # For integral matrices, rank_F2 <= rank_Q.  The stored replay has
        # MN=0 and zero F2 middle residue for every triple, so neither
        # rational rank can increase without violating rank_N+rank_M<=dim C1.
        rational_histogram = Counter(f2_histogram)
        rank_replay_source = "authenticated_source_rank_replay_with_integral_exactness_lift"
    else:
        f2_histogram = Counter()
        rational_histogram = Counter()
        for profile_triple in product(sorted(profile_bad), repeat=3):
            f2_result, rational_result = pair_rank(
                simplices,
                simplicial_bad,
                simplicial_infinity,
                profile_triple,
            )
            f2_histogram[f2_result] += 1
            rational_histogram[rational_result] += 1
        rank_replay_source = "recomputed_from_signed_integral_complex"

    intersections = {}
    masks = sorted(profile_bad)
    for size in range(1, 4):
        for chosen in combinations(masks, size):
            selected = set.intersection(*(profile_bad[mask] for mask in chosen))
            key = ",".join(map(str, chosen))
            intersections[key] = subcomplex_summary(record, selected)

    component_maps = []
    for size in (2, 3):
        for chosen in combinations(masks, size):
            child_key = ",".join(map(str, chosen))
            child = intersections[child_key]
            for omitted in range(size):
                parent_tuple = chosen[:omitted] + chosen[omitted + 1 :]
                parent_key = ",".join(map(str, parent_tuple))
                parent = intersections[parent_key]
                mapping = [
                    [component["id"], component_target(parent, component["vertices"][0])]
                    for component in child["components"]
                ]
                component_maps.append({
                    "source": child_key,
                    "target": parent_key,
                    "component_map": mapping,
                })

    f2_histogram_rows = [
        {"result": list(result), "ordered_profile_triples": count}
        for result, count in sorted(f2_histogram.items())
    ]
    rational_histogram_rows = [
        {"result": list(result), "ordered_profile_triples": count}
        for result, count in sorted(rational_histogram.items())
    ]
    return {
        "source_sha256": file_sha256(path),
        "source_format": record["format"],
        "master_cell_count": len(record["cells"]),
        "strict_closure_pair_count": len(record["strict_closure_pairs"]),
        "strict_three_cell_chain_count": len(record["strict_three_cell_chains"]),
        "profile_count": len(profiles),
        "profile_source": profile_source,
        "simplicialization": simplicialization,
        "rank_replay_source": rank_replay_source,
        "ordered_profile_triple_count": sum(f2_histogram.values()),
        "profile_intersections_through_order_three": intersections,
        "component_specialization_maps": component_maps,
        "maximum_intersection_component_count": max(
            summary["component_count"] for summary in intersections.values()
        ),
        "nontrivial_split_merge_exercised": any(
            summary["component_count"] > 1 for summary in intersections.values()
        ),
        "balanced_pair_rank_histogram_f2": f2_histogram_rows,
        "balanced_pair_rank_histogram_q": rational_histogram_rows,
        "all_ordered_profile_triples_middle_exact_f2": all(
            result[3] == 0 for result in f2_histogram
        ),
        "all_ordered_profile_triples_middle_exact_q": all(
            result[3] == 0 for result in rational_histogram
        ),
        "scope_boundary_retained_as_ordinary": bool(record.get("scope_boundary_subcomplex")),
        "parent_infinity_cell_count": len(record["parent_infinity_subcomplex"]),
        "parent_infinity_interpretation": (
            "declared_schema_relative_interface_only"
            if record.get("status") == "SCHEMA_CANARY"
            else "empty_local_fixture_declaration"
        ),
    }


def two_support_audit() -> dict:
    records = {name: read_json(path) for name, path in TWO_SUPPORT_INPUTS.items()}
    missing = {
        name: [field for field in REQUIRED_COMPILER_FIELDS if field not in record]
        for name, record in records.items()
    }
    gate = records["gate"]
    open_cells = records["open_t_open_u"]["open_cell_v_lift"]
    open_sections = records["open_t_algebraic_u"]["cumulative_open_t_algebraic_u_section_v_lift"]
    algebraic_final = records["algebraic_t_final_u"]["cumulative_algebraic_t_v_lift"]
    base_cells = (
        int(open_cells["open_base_cells"])
        + int(open_sections["completed_sections"])
        + int(algebraic_final["base_cells"])
    )
    lifted = (
        int(open_cells["lifted_cells"])
        + int(open_sections["lifted_cells"])
        + int(algebraic_final["lifted_cells"])
    )
    return {
        "source_sha256": {
            name: file_sha256(path) for name, path in TWO_SUPPORT_INPUTS.items()
        },
        "covered_parent_supports": [domain["support"] for domain in gate["parent_domains"]],
        "base_cell_partition": {
            "open_t_open_u": int(open_cells["open_base_cells"]),
            "open_t_algebraic_u": int(open_sections["completed_sections"]),
            "algebraic_t": int(algebraic_final["base_cells"]),
            "total": base_cells,
        },
        "lifted_cell_partition": {
            "open_t_open_u": int(open_cells["lifted_cells"]),
            "open_t_algebraic_u": int(open_sections["lifted_cells"]),
            "algebraic_t": int(algebraic_final["lifted_cells"]),
            "total": lifted,
        },
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


def semantic_digest(payload) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def fixture_limit_census(canary_replay: dict) -> dict:
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
    }


def main() -> None:
    canary_replay = {
        "schema_relative": canary_component_cosheaf(CANARIES["schema_relative"]),
        "transverse_node": canary_component_cosheaf(CANARIES["transverse_node"]),
        "multibox": canary_component_cosheaf(CANARIES["multibox"]),
        "first_event": canary_component_cosheaf(CANARIES["first_event"]),
    }
    support_audit = two_support_audit()
    core = {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "pilot_supports": [[3, 1, 15], [3, 3, 7]],
            "honest_9dvl_score": "2/9",
            "pair_branch_closed": False,
            "triple_branch_closed": False,
        },
        "method_contract": {
            "roadmap_role": "certify connected-component incidence only",
            "first_betti_role": "retain overlap, two-cell, and signed frontier data; a graph alone is insufficient",
            "cosheaf_role": "compress only after a certified face poset and specialization maps exist",
            "split_merge_role": "promotion requires a fixture with a nontrivial component split or merge",
            "infinity_role": "use the genuine parent-infinity subcomplex in the relative complex",
            "morse_role": "post-certificate compression only",
        },
        "canary_replay": canary_replay,
        "fixture_limit_census": fixture_limit_census(canary_replay),
        "two_support_input_audit": support_audit,
        "decision": {
            "promote_existing_manifests_as_master_closure_replacement": False,
            "result": STATUS,
            "no_go_scope": "reuse completed two-support lift manifests as global component-cosheaf input without new closure construction",
            "boundary_aware_roadmap_method": "OPEN_EXPERIMENT_NOT_TESTED_ON_EITHER_SUPPORT",
            "reason": "the completed fiber inventories do not encode closure-complete component specialization, complete bad-signature labels, or true-infinity incidence",
            "safe_reuse": "use component/cosheaf reduction after the master closure compiler emits the missing incidence contract",
            "next_pair_action": "compile exact face-compatible closure and signature labels across the completed two-support fibers, beginning with the section-960 collision and section-550 endpoint-tangency stars",
            "next_triple_action": "retain the independently selected boundary-complete projection-critical roadmap route",
        },
        "citations": [
            "Basu-Pollack-Roy arXiv:math/0603248",
            "Basu-Roy Divide and Conquer Roadmap for Algebraic Sets",
            "Kishimoto-Yushima arXiv:2202.03659",
            "Forman, Morse Theory for Cell Complexes, Adv. Math. 134 (1998)",
        ],
        "verifier": {
            "command": "python ai/omreal/verify_diag3_component_cosheaf_pilot.py",
            "hostile_mutations_required": 14,
        },
    }
    core["semantic_sha256"] = semantic_digest(core)
    OUTPUT.write_text(json.dumps(core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("WROTE", OUTPUT)
    print("STATUS", STATUS)
    print("TWO_SUPPORT_LIFTED_CELLS", support_audit["lifted_cell_partition"]["total"])
    print("SEMANTIC_SHA256", core["semantic_sha256"])


if __name__ == "__main__":
    main()
