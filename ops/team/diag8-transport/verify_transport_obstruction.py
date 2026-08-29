#!/usr/bin/env python3
"""Exact replay for the diagonal-eight certificate-transport no-go.

The checker is standard-library only.  It independently enumerates every
tope of three rational central arrangements by restriction recursion.  Every
enumerated tope carries an exact integer witness, while the recursion proves
coverage.  No catalog, floating-point solver, mutation-tree route, or
partial-cube premise is used.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "TRANSPORT_COUNTERMODELS.json"
EXPECTED_FORMAT = "diag8-certificate-transport-countermodels-v1"

PINNED_INPUTS = {
    "ai/omreal/PARENT_CONTRACTIBILITY_AUDIT.md":
        "d0fde0f211db71228a48af3c928a213181bab4bb29c25a57d2ed7417f49de226",
    "ai/omreal/WALK_THEORY.md":
        "820cf256706d0e18a927cbb58758354ca433f15f249c8ebaeaf018fd37a1c7c2",
    "ai/omreal/verify_mutation_graph_not_partial_cube.py":
        "cf444dac9bd386a16e9d25171069f076edcde2ffafd416bad375e5f99b131bea",
    "ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md":
        "64896fa28a76f57344bd246f1546322e1361f6ac57f164ca6199c58938c30903",
}


def determinant(matrix):
    matrix = tuple(tuple(map(int, row)) for row in matrix)
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant(
            tuple(row[:column] + row[column + 1 :] for row in matrix[1:])
        )
        for column, value in enumerate(matrix[0])
    )


def primitive(vector):
    vector = tuple(map(int, vector))
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    divisor = max(divisor, 1)
    return tuple(value // divisor for value in vector)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def ordered_subsets(n, size):
    return tuple(
        sorted(combinations(range(n), size), key=lambda subset: tuple(reversed(subset)))
    )


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
    for index in range(1, len(values)):
        cursor = index
        while cursor and values[cursor - 1] > values[cursor]:
            values[cursor - 1], values[cursor] = values[cursor], values[cursor - 1]
            sign = -sign
            cursor -= 1
    return tuple(values), sign


def compile_extension_system(parent_signs):
    """Compile every GP constraint involving a ninth labeled element."""
    parent_bits = tuple(value > 0 for value in parent_signs)
    new_bases = colex_subsets(8, 3)
    new_index = {basis: index for index, basis in enumerate(new_bases)}
    parent_index = {
        basis: index for index, basis in enumerate(colex_subsets(8, 4))
    }
    by_last = [[] for _basis in new_bases]
    for common in combinations(range(1, 10), 2):
        rest = [element for element in range(1, 10) if element not in common]
        for a, b, c, d in combinations(rest, 4):
            if 9 not in common and 9 not in (a, b, c, d):
                continue
            terms = []
            for pairs, explicit_minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                variables = []
                constant = explicit_minus
                for left, right in pairs:
                    basis, alternating_sign = sort_with_sign(common + (left, right))
                    constant ^= alternating_sign < 0
                    if 9 in basis:
                        triple = tuple(element for element in basis if element != 9)
                        variables.append(new_index[triple])
                    else:
                        constant ^= int(parent_bits[parent_index[basis]])
                terms.append((tuple(variables), int(constant)))
            last = max(variable for variables, _constant in terms for variable in variables)
            by_last[last].append(tuple(terms))
    return tuple(tuple(rows) for rows in by_last)


def enumerate_extensions(parent_signs):
    """Exact GP backtracking over all uniform one-element extensions."""
    by_last = compile_extension_system(parent_signs)
    values = [0] * len(by_last)
    next_value = [0] * len(by_last)
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
        elif depth == len(by_last) - 1:
            signatures.append(
                sum(value << variable for variable, value in enumerate(values))
            )
            next_value[depth] += 1
        else:
            depth += 1
            next_value[depth] = 0
    return tuple(signatures)


def bracket(columns, basis):
    return determinant(
        tuple(tuple(columns[column][row] for column in basis) for row in range(4))
    )


def parent_signs(columns):
    answer = []
    for basis in ordered_subsets(len(columns), 4):
        value = bracket(columns, basis)
        if value == 0:
            raise AssertionError(f"nonuniform parent at {basis}")
        answer.append(1 if value > 0 else -1)
    return tuple(answer)


def sign_mask(signs):
    return sum((value > 0) << index for index, value in enumerate(signs))


def derived_rows(columns):
    rows = []
    for triple in ordered_subsets(len(columns), 3):
        coordinate_rows = tuple(
            tuple(columns[column][row] for column in triple) for row in range(4)
        )
        normal = []
        for coordinate in range(4):
            minor = tuple(
                row for row_index, row in enumerate(coordinate_rows)
                if row_index != coordinate
            )
            normal.append((-1) ** (coordinate + 3) * determinant(minor))
        rows.append(primitive(normal))
    if any(not any(row) for row in rows):
        raise AssertionError("uniform parent produced a zero derived normal")
    return tuple(rows)


def restrict_rows(rows, normal):
    dimension = len(normal)
    pivot = next(index for index, value in enumerate(normal) if value)
    free = tuple(index for index in range(dimension) if index != pivot)
    pivot_value = normal[pivot]
    restricted = tuple(
        primitive(
            tuple(
                pivot_value * row[index] - row[pivot] * normal[index]
                for index in free
            )
        )
        for row in rows
    )
    return restricted, pivot, free


def lift_restricted(witness, normal, pivot, free):
    vector = [0] * len(normal)
    pivot_value = normal[pivot]
    for index, value in zip(free, witness):
        vector[index] = pivot_value * value
    vector[pivot] = -sum(
        normal[index] * value for index, value in zip(free, witness)
    )
    answer = primitive(vector)
    if dot(normal, answer) != 0:
        raise AssertionError("restriction lift missed the new hyperplane")
    return answer


def enumerate_topes(rows, dimension=4):
    """Exact restriction recursion; returns sign bitset -> integer witness."""
    rows = tuple(primitive(row) for row in rows)
    if any(len(row) != dimension for row in rows):
        raise AssertionError("row dimensions disagree")
    if any(not any(row) for row in rows):
        return {}
    if not rows:
        return {0: (1,) + (0,) * (dimension - 1)}
    if dimension == 1:
        positive = sum((row[0] > 0) << index for index, row in enumerate(rows))
        negative = ((1 << len(rows)) - 1) ^ positive
        return {positive: (1,), negative: (-1,)}

    topes = {0: (1,) + (0,) * (dimension - 1)}
    for index, normal in enumerate(rows):
        restricted, pivot, free = restrict_rows(rows[:index], normal)
        boundary = {
            signs: lift_restricted(witness, normal, pivot, free)
            for signs, witness in enumerate_topes(
                restricted, dimension=dimension - 1
            ).items()
        }
        next_topes = {}
        for signs, witness in topes.items():
            if signs in boundary:
                continue
            value = dot(normal, witness)
            if value == 0:
                raise AssertionError("nonsplit witness lies on the new wall")
            next_topes[signs | ((value > 0) << index)] = witness

        for signs, wall_witness in boundary.items():
            scale = 1
            for old_row in rows[:index]:
                margin = dot(old_row, wall_witness)
                slope = dot(old_row, normal)
                if margin == 0:
                    raise AssertionError("restricted witness is not strict")
                if slope:
                    scale = max(scale, abs(slope) // abs(margin) + 1)
            positive = primitive(
                scale * value + slope
                for value, slope in zip(wall_witness, normal)
            )
            negative = primitive(
                scale * value - slope
                for value, slope in zip(wall_witness, normal)
            )
            if dot(normal, positive) <= 0 or dot(normal, negative) >= 0:
                raise AssertionError("wall perturbation has the wrong side")
            next_topes[signs | (1 << index)] = positive
            next_topes[signs] = negative
        topes = next_topes
    return topes


def verify_witness(rows, signs, witness):
    if len(witness) != 4 or not any(witness):
        raise AssertionError("bad tope witness")
    for index, row in enumerate(rows):
        wanted = 1 if signs & (1 << index) else -1
        if wanted * dot(row, witness) <= 0:
            raise AssertionError(f"tope witness fails row {index}")


def verify_all_witnesses(rows, topes):
    for signs, witness in topes.items():
        verify_witness(rows, signs, witness)


def semantic_digest(signatures, width):
    digest = sha256()
    for signature in sorted(signatures):
        digest.update(int(signature).to_bytes(width, "little"))
    return digest.hexdigest()


def expect_failure(function, *args):
    try:
        function(*args)
    except AssertionError:
        return
    raise AssertionError("deliberately invalid transport canary was accepted")


def require_common_label(source, target, signature):
    if signature not in source or signature not in target:
        raise AssertionError("claimed common feasibility label is born or dies")


def require_injective_label_map(pairs):
    values = [target for _source, target in pairs]
    if len(values) != len(set(values)):
        raise AssertionError("deletion label map is not injective")


def require_infinity_pair_map(source, target, cell_map):
    image = {cell_map[cell] for cell in source}
    if image != set(target):
        raise AssertionError("transport changes the true-infinity subcomplex")


def gf2_rank(columns):
    pivots = {}
    for column in columns:
        value = int(column)
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def graph_relative_h1(vertices, edges, infinity_vertices):
    retained = tuple(vertex for vertex in vertices if vertex not in infinity_vertices)
    row = {vertex: index for index, vertex in enumerate(retained)}
    boundary_columns = []
    for left, right in edges:
        column = 0
        if left in row:
            column ^= 1 << row[left]
        if right in row:
            column ^= 1 << row[right]
        boundary_columns.append(column)
    return len(edges) - gf2_rank(boundary_columns)


def verify_inputs():
    for relative, expected in PINNED_INPUTS.items():
        actual = sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError(f"pinned input changed: {relative} -> {actual}")


def verify_mutation(record):
    fixed = tuple(tuple(column) for column in record["fixed_columns"])
    wall = tuple(record["wall_column"])
    minus_column = tuple(record["minus_column"])
    plus_column = tuple(record["plus_column"])
    if tuple((left + right) // 2 for left, right in zip(minus_column, plus_column)) != wall:
        raise AssertionError("wall column is not the path midpoint")

    minus = fixed + (minus_column,)
    plus = fixed + (plus_column,)
    wall_parent = fixed + (wall,)
    bases = ordered_subsets(8, 4)
    minus_signs = parent_signs(minus)
    plus_signs = parent_signs(plus)
    changed = tuple(
        basis for basis, left, right in zip(bases, minus_signs, plus_signs)
        if left != right
    )
    if changed != (tuple(record["flipped_basis"]),):
        raise AssertionError(f"not a one-basis mutation: {changed}")
    wall_zeros = tuple(basis for basis in bases if bracket(wall_parent, basis) == 0)
    if wall_zeros != changed:
        raise AssertionError(f"mutation wall has additional zeros: {wall_zeros}")
    if sign_mask(minus_signs) != int(record["minus_parent_sign_mask"], 16):
        raise AssertionError("minus parent signs changed")
    if sign_mask(plus_signs) != int(record["plus_parent_sign_mask"], 16):
        raise AssertionError("plus parent signs changed")

    minus_extensions = enumerate_extensions(minus_signs)
    plus_extensions = enumerate_extensions(plus_signs)
    if len(minus_extensions) != record["minus_abstract_extension_count"]:
        raise AssertionError("minus abstract-extension count changed")
    if len(plus_extensions) != record["plus_abstract_extension_count"]:
        raise AssertionError("plus abstract-extension count changed")
    if semantic_digest(minus_extensions, 7) != record["minus_abstract_extension_digest"]:
        raise AssertionError("minus abstract-extension digest changed")
    if semantic_digest(plus_extensions, 7) != record["plus_abstract_extension_digest"]:
        raise AssertionError("plus abstract-extension digest changed")
    minus_extension_set = set(minus_extensions)
    plus_extension_set = set(plus_extensions)
    extension_common = minus_extension_set & plus_extension_set
    extension_deaths = minus_extension_set - plus_extension_set
    extension_births = plus_extension_set - minus_extension_set
    if (len(extension_common), len(extension_deaths), len(extension_births)) != (
        record["common_abstract_extension_count"],
        record["abstract_extension_death_count"],
        record["abstract_extension_birth_count"],
    ):
        raise AssertionError("abstract-extension birth/death census changed")
    abstract_death = int(record["abstract_death_signature"], 16)
    abstract_birth = int(record["abstract_birth_signature"], 16)
    if abstract_death not in extension_deaths or abstract_birth not in extension_births:
        raise AssertionError("pinned abstract extension birth/death changed")
    expect_failure(
        require_common_label, minus_extension_set, plus_extension_set, abstract_death
    )
    expect_failure(
        require_common_label, minus_extension_set, plus_extension_set, abstract_birth
    )

    minus_rows = derived_rows(minus)
    plus_rows = derived_rows(plus)
    minus_topes = enumerate_topes(minus_rows)
    plus_topes = enumerate_topes(plus_rows)
    verify_all_witnesses(minus_rows, minus_topes)
    verify_all_witnesses(plus_rows, plus_topes)
    if len(minus_topes) != record["minus_tope_count"]:
        raise AssertionError("minus tope count changed")
    if len(plus_topes) != record["plus_tope_count"]:
        raise AssertionError("plus tope count changed")
    if semantic_digest(minus_topes, 7) != record["minus_tope_digest"]:
        raise AssertionError("minus tope digest changed")
    if semantic_digest(plus_topes, 7) != record["plus_tope_digest"]:
        raise AssertionError("plus tope digest changed")

    common = set(minus_topes) & set(plus_topes)
    deaths = set(minus_topes) - set(plus_topes)
    births = set(plus_topes) - set(minus_topes)
    if (len(common), len(deaths), len(births)) != (
        record["common_tope_count"], record["death_count"], record["birth_count"]
    ):
        raise AssertionError("mutation birth/death census changed")

    death = int(record["death_signature"], 16)
    birth = int(record["birth_signature"], 16)
    death_witness = tuple(record["death_witness"])
    birth_witness = tuple(record["birth_witness"])
    if death not in deaths or minus_topes[death] != death_witness:
        raise AssertionError("declared death is not the exact enumerated death")
    if birth not in births or plus_topes[birth] != birth_witness:
        raise AssertionError("declared birth is not the exact enumerated birth")
    verify_witness(minus_rows, death, death_witness)
    verify_witness(plus_rows, birth, birth_witness)

    # Hostile transport claims must fail closed on both sides of the event.
    expect_failure(require_common_label, minus_topes, plus_topes, birth)
    expect_failure(require_common_label, minus_topes, plus_topes, death)
    return (
        len(minus_extensions),
        len(plus_extensions),
        len(minus_topes),
        len(plus_topes),
        len(deaths),
        len(births),
    )


def verify_reducible_deletion(record):
    base = tuple(tuple(column) for column in record["base_columns"])
    order = tuple(record["lexicographic_order"])
    scale = int(record["scale"])
    # Written without any floating epsilon: N^3 v6 + N^2 v5 + N v4 + v3.
    extension = tuple(
        sum(
            scale ** (len(order) - 1 - index) * base[element][coordinate]
            for index, element in enumerate(order)
        )
        for coordinate in range(4)
    )
    if extension != tuple(record["extension_column"]):
        raise AssertionError("lexicographic extension column changed")
    full = base + (extension,)
    parent_signs(full)

    # Check the finite chirotope identity defining the lexicographic extension.
    for triple in combinations(range(7), 3):
        actual = bracket(full, triple + (7,))
        expected = None
        for element in order:
            candidate = bracket(full, triple + (element,))
            if candidate:
                expected = 1 if candidate > 0 else -1
                break
        if expected is None or (1 if actual > 0 else -1) != expected:
            raise AssertionError(f"not the declared lexicographic extension at {triple}")

    full_rows = derived_rows(full)
    full_topes = enumerate_topes(full_rows)
    verify_all_witnesses(full_rows, full_topes)
    if len(full_topes) != record["full_tope_count"]:
        raise AssertionError("lexicographic-parent tope count changed")
    if semantic_digest(full_topes, 7) != record["full_tope_digest"]:
        raise AssertionError("lexicographic-parent tope digest changed")

    triples8 = ordered_subsets(8, 3)
    retained = tuple(index for index, triple in enumerate(triples8) if 7 not in triple)
    groups = defaultdict(list)
    for signature in full_topes:
        projected = sum(
            ((signature >> old_index) & 1) << new_index
            for new_index, old_index in enumerate(retained)
        )
        groups[projected].append(signature)

    deletion_rows = derived_rows(base)
    deletion_topes = enumerate_topes(deletion_rows)
    verify_all_witnesses(deletion_rows, deletion_topes)
    if set(groups) != set(deletion_topes):
        raise AssertionError("deletion projections do not equal all deletion topes")
    if len(deletion_topes) != record["deletion_tope_count"]:
        raise AssertionError("deletion tope count changed")
    if len(groups) != record["projected_label_count"]:
        raise AssertionError("projected label count changed")
    if semantic_digest(groups, 5) != record["projected_tope_digest"]:
        raise AssertionError("projected tope digest changed")
    if sum(len(fiber) > 1 for fiber in groups.values()) != record["nontrivial_fiber_count"]:
        raise AssertionError("nontrivial deletion-fiber count changed")
    if max(map(len, groups.values())) != record["maximum_fiber_size"]:
        raise AssertionError("maximum deletion-fiber size changed")

    left = int(record["collision_signature_a"], 16)
    right = int(record["collision_signature_b"], 16)
    projected = int(record["collision_projected_signature"], 16)
    if left == right or left not in groups[projected] or right not in groups[projected]:
        raise AssertionError("declared deletion label collision disappeared")
    differing = tuple(
        triples8[index] for index in range(len(triples8))
        if (left ^ right) & (1 << index)
    )
    if differing != tuple(map(tuple, record["collision_differing_triples"])):
        raise AssertionError("deletion collision coordinates changed")
    if full_topes[left] != tuple(record["collision_witness_a"]):
        raise AssertionError("first deletion-collision witness changed")
    if full_topes[right] != tuple(record["collision_witness_b"]):
        raise AssertionError("second deletion-collision witness changed")
    expect_failure(require_injective_label_map, ((left, projected), (right, projected)))
    return len(full_topes), len(deletion_topes), len(groups), max(map(len, groups.values()))


def verify_finite_topology(record):
    vertices = tuple(record["vertices"])
    edges = tuple(map(tuple, record["cycle_edges"]))
    source_infinity = set(record["source_infinity_vertices"])
    target_infinity = set(record["target_infinity_vertices"])
    source_h1 = graph_relative_h1(vertices, edges, source_infinity)
    target_h1 = graph_relative_h1(vertices, edges, target_infinity)
    if source_h1 != record["source_relative_h1_f2"]:
        raise AssertionError("source relative H1 changed")
    if target_h1 != record["target_relative_h1_f2"]:
        raise AssertionError("target relative H1 changed")
    identity = {vertex: vertex for vertex in vertices}
    expect_failure(
        require_infinity_pair_map, source_infinity, target_infinity, identity
    )

    boundary_rank = gf2_rank(
        tuple((1 << left) ^ (1 << right) for left, right in edges)
    )
    cycle_nullity = len(edges) - boundary_rank
    unfilled_h1 = cycle_nullity
    filled_h1 = cycle_nullity - gf2_rank(((1 << len(edges)) - 1,))
    if unfilled_h1 != record["unfilled_node_h1_f2"]:
        raise AssertionError("unfilled node model changed")
    if filled_h1 != record["filled_node_h1_f2"]:
        raise AssertionError("filled node model changed")
    return source_h1, target_h1, unfilled_h1, filled_h1


def main():
    verify_inputs()
    certificate = json.loads(CERTIFICATE.read_text())
    if certificate.get("format") != EXPECTED_FORMAT:
        raise AssertionError("wrong certificate format")
    if certificate["canonical_base"] != {
        "revision": "5393b03fda623dc6b4552130d13467fae71d31bc",
        "tree": "06cc3363a021b8adc59e66865f44bf8eafa66029",
    }:
        raise AssertionError("canonical base changed")

    mutation = verify_mutation(certificate["mutation"])
    deletion = verify_reducible_deletion(certificate["reducible_deletion"])
    topology = verify_finite_topology(certificate["finite_topology"])

    print("PASS pinned canonical inputs 4/4")
    print(
        "PASS exact one-bracket mutation: abstract extensions %d -> %d; "
        "topes %d -> %d, deaths %d, births %d"
        % mutation
    )
    print(
        "PASS exact reducible lex deletion: full %d, deletion %d, projected %d, max fiber %d"
        % deletion
    )
    print(
        "PASS exact topology canaries: infinity-relative H1 %d -> %d; node H1 %d -> %d"
        % topology
    )
    print("PASS canaries mutation_birth, mutation_death, infinity_change, label_collision")
    print("THEOREM edge-wise labeled stratified-pair isomorphism is sufficient for transport")
    print("NO-GO mutation connectivity and reducible deletion do not supply that isomorphism")
    print("SCOPE no all-parent coverage and no 9DVL ledger change")


if __name__ == "__main__":
    main()
