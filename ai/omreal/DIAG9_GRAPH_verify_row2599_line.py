#!/usr/bin/env python3
"""Exact 26-cell labeled residual roadmap on a row-2599 coordinate line.

This extends the minimal two-cell slice certificate across -1/2 < t < 1/2.
Twenty-five disjoint rational isolating boxes cover every root of every one
of the 84,840 labeled residual determinant polynomials.  A polynomial gcd
inside each box proves that all occurrences assigned to that box share one
algebraic crossing parameter.  Exact tope recursion labels all 26 open cells.

The certificate is complete for this coordinate line only.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_exact_topes as topes
import DIAG9_GRAPH_verify_row2599_slice as slice_verify


HERE = Path(__file__).resolve().parent
ROADMAP = HERE / "data" / "DIAG9_GRAPH_row2599_line_roadmap.npz"
GRAPH = HERE / "data" / "DIAG9_GRAPH_row2599_line_graph.npz"
FORMAT = "diag9-row2599-r2c7-line-v1"
GRAPH_FORMAT = "diag9-labeled-master-tree-v1"
SEGMENT = (Fraction(-1, 2), Fraction(1, 2))
BOX_RADIUS = Fraction(1, 10**9)
CENTER_TEXT = (
    "-0.484925184344539",
    "-0.399019445608111",
    "-0.270711637470779",
    "-0.266249157223290",
    "-0.144266748423946",
    "-0.126232183098092",
    "-0.102149712960872",
    "-0.0767516986969422",
    "-0.0491305481015578",
    "-0.0179946549768344",
    "-0.00206169133271415",
    "0.0208672348092365",
    "0.0514343627455221",
    "0.0686072134553845",
    "0.102781285416638",
    "0.108409541265180",
    "0.122071634070562",
    "0.124110903647882",
    "0.146682865333058",
    "0.161759963723391",
    "0.190549797157969",
    "0.206707776855004",
    "0.345241771463128",
    "0.410593188625252",
    "0.451364050316009",
)
BOXES = tuple(
    (Fraction(center) - BOX_RADIUS, Fraction(center) + BOX_RADIUS)
    for center in CENTER_TEXT
)


def normalize_monic(polynomial):
    polynomial = slice_verify.trim(polynomial)
    if not polynomial:
        return ()
    leading = polynomial[-1]
    return tuple(coefficient / leading for coefficient in polynomial)


def polynomial_gcd(left, right):
    left = slice_verify.trim(left)
    right = slice_verify.trim(right)
    while right:
        left, right = right, slice_verify.polynomial_divrem(left, right)
    return normalize_monic(left)


def common_gcd(polynomials):
    answer = tuple(polynomials[0])
    for polynomial in polynomials[1:]:
        answer = polynomial_gcd(answer, polynomial)
        if len(answer) <= 1:
            break
    return answer


def samples_from_boxes():
    samples = [(SEGMENT[0] + BOXES[0][0]) / 2]
    samples.extend(
        (left_box[1] + right_box[0]) / 2
        for left_box, right_box in zip(BOXES, BOXES[1:])
    )
    samples.append((BOXES[-1][1] + SEGMENT[1]) / 2)
    return tuple(samples)


SAMPLES = samples_from_boxes()


def wall_groups(base):
    if len(BOXES) != 25:
        raise AssertionError("wrong isolating-box count")
    if not all(
        SEGMENT[0] < left < right < SEGMENT[1] for left, right in BOXES
    ):
        raise AssertionError("wall box leaves coordinate segment")
    if not all(left[1] < right[0] for left, right in zip(BOXES, BOXES[1:])):
        raise AssertionError("wall isolating boxes overlap")

    intercept, slope = slice_verify.slice_polynomials(base)
    groups = [[] for _ in BOXES]
    polynomials = [[] for _ in BOXES]
    global_occurrences = 0
    for fourset in slice_verify.residual_foursets():
        polynomial = slice_verify.derived_polynomial(fourset, intercept, slope)
        if not polynomial:
            raise AssertionError("coordinate line is contained in a residual wall")
        total = slice_verify.root_count(polynomial, *SEGMENT)
        if not total:
            continue
        global_occurrences += total
        local = [
            slice_verify.root_count(polynomial, left, right)
            for left, right in BOXES
        ]
        if sum(local) != total:
            raise AssertionError("isolating boxes do not cover a residual root")
        for index, count in enumerate(local):
            if count not in (0, 1):
                raise AssertionError("one wall box contains repeated occurrence roots")
            if count:
                groups[index].append(fourset)
                polynomials[index].append(polynomial)

    if global_occurrences != 89:
        raise AssertionError(f"expected 89 labeled roots, found {global_occurrences}")
    if any(not group for group in groups):
        raise AssertionError("empty proposed wall box")

    gcds = []
    for box, group_polynomials in zip(BOXES, polynomials):
        divisor = common_gcd(group_polynomials)
        if len(divisor) <= 1 or slice_verify.root_count(divisor, *box) != 1:
            raise AssertionError("wall occurrences do not share one algebraic root")
        derivative = tuple(
            index * divisor[index] for index in range(1, len(divisor))
        )
        if slice_verify.root_count(derivative, *box):
            raise AssertionError("geometric wall root is not simple")
        for polynomial in group_polynomials:
            repeated_factor = polynomial_gcd(
                polynomial,
                tuple(
                    index * polynomial[index]
                    for index in range(1, len(polynomial))
                ),
            )
            if slice_verify.root_count(repeated_factor, *box):
                raise AssertionError("a labeled residual occurrence is tangent")
        gcds.append(divisor)
    return tuple(tuple(group) for group in groups), tuple(gcds)


def enumerate_cell_topes(base):
    answer = []
    expected = slice_verify.expected_parent_signs()
    for index, parameter in enumerate(SAMPLES):
        matrix = slice_verify.scaled_parent(base, parameter)
        if topes.parent_signs(matrix) != expected:
            raise AssertionError(f"cell sample {index} leaves parent 2599")
        rows = topes.derived_rows(matrix)
        chamber_topes = topes.enumerate_topes(rows, dimension=4)
        topes.verify_topes(rows, chamber_topes)
        if len(chamber_topes) != 26_112:
            raise AssertionError(f"cell {index} has wrong generic tope count")
        answer.append(tuple(sorted(chamber_topes)))
        print(f"  exact cell labels {index + 1}/{len(SAMPLES)}", flush=True)
    return tuple(answer)


def signature_patterns(cell_topes):
    patterns = {}
    for cell, signatures in enumerate(cell_topes):
        bit = 1 << cell
        for signature in signatures:
            patterns[signature] = patterns.get(signature, 0) | bit
    full = (1 << len(cell_topes)) - 1
    proper = tuple(sorted(set(patterns.values()) - {0, full}))
    return patterns, proper


def support_matrix(patterns):
    return np.asarray(
        tuple(
            tuple((pattern >> cell) & 1 for cell in range(len(SAMPLES)))
            for pattern in patterns
        ),
        dtype=np.uint8,
    )


def verify_interval_structure(patterns):
    """Verify the complete signature supports are intervals on the line.

    This is a statement about restrictions of signatures to this certified
    coordinate line.  It neither identifies equal restricted supports with
    equal global feasibility regions nor infers global region inclusion.
    """
    cell_count = len(SAMPLES)
    full = (1 << cell_count) - 1
    expected_proper = {
        (1 << split) - 1 for split in range(1, cell_count)
    } | {
        full ^ ((1 << split) - 1) for split in range(1, cell_count)
    }
    multiplicity = Counter(patterns.values())
    observed_proper = set(multiplicity) - {full}
    if observed_proper != expected_proper:
        raise AssertionError("signature supports are not exactly prefixes/suffixes")
    if multiplicity[full] != 25_992:
        raise AssertionError("wrong all-line signature count")
    if sum(multiplicity[pattern] for pattern in observed_proper) != 240:
        raise AssertionError("wrong proper-on-line signature count")
    exceptional = sorted(
        multiplicity[pattern]
        for pattern in observed_proper
        if multiplicity[pattern] != 2
    )
    if exceptional != [72, 72]:
        raise AssertionError("wrong support-pattern multiplicity distribution")
    return expected_proper


def build():
    base = slice_verify.source_parent()
    expected = slice_verify.expected_parent_signs()
    for endpoint in SEGMENT:
        if topes.parent_signs(slice_verify.scaled_parent(base, endpoint)) != expected:
            raise AssertionError("line endpoint leaves parent 2599")
    groups, gcds = wall_groups(base)
    cell_topes = enumerate_cell_topes(base)
    patterns, proper = signature_patterns(cell_topes)
    verify_interval_structure(patterns)

    offsets = [0]
    flat_groups = []
    for group in groups:
        flat_groups.extend(group)
        offsets.append(len(flat_groups))
    gcd_offsets = [0]
    gcd_numerators = []
    gcd_denominators = []
    for polynomial in gcds:
        gcd_numerators.extend(value.numerator for value in polynomial)
        gcd_denominators.extend(value.denominator for value in polynomial)
        gcd_offsets.append(len(gcd_numerators))

    np.savez_compressed(
        ROADMAP,
        format=np.asarray(FORMAT),
        parent_index=np.asarray(slice_verify.PARENT_INDEX, dtype=np.int64),
        source_chart=np.asarray(slice_verify.SOURCE_CHART, dtype=np.int64),
        varying_position=np.asarray(
            (slice_verify.VARYING_ROW, slice_verify.VARYING_COLUMN), dtype=np.int8
        ),
        segment_num=np.asarray(tuple(value.numerator for value in SEGMENT), dtype=np.int64),
        segment_den=np.asarray(tuple(value.denominator for value in SEGMENT), dtype=np.int64),
        box_lo_num=np.asarray(tuple(left.numerator for left, _ in BOXES), dtype=np.int64),
        box_lo_den=np.asarray(tuple(left.denominator for left, _ in BOXES), dtype=np.int64),
        box_hi_num=np.asarray(tuple(right.numerator for _, right in BOXES), dtype=np.int64),
        box_hi_den=np.asarray(tuple(right.denominator for _, right in BOXES), dtype=np.int64),
        sample_num=np.asarray(tuple(value.numerator for value in SAMPLES), dtype=np.int64),
        sample_den=np.asarray(tuple(value.denominator for value in SAMPLES), dtype=np.int64),
        wall_offset=np.asarray(offsets, dtype=np.uint16),
        wall_fourset=np.asarray(flat_groups, dtype=np.uint8),
        gcd_offset=np.asarray(gcd_offsets, dtype=np.uint16),
        gcd_numerator=np.asarray(tuple(map(str, gcd_numerators))),
        gcd_denominator=np.asarray(tuple(map(str, gcd_denominators))),
        cell_tope=np.asarray(cell_topes, dtype=np.uint64),
        signature=np.asarray(tuple(sorted(patterns)), dtype=np.uint64),
        signature_pattern=np.asarray(
            tuple(patterns[signature] for signature in sorted(patterns)), dtype=np.uint32
        ),
    )

    edges = tuple((index, index + 1) for index in range(len(SAMPLES) - 1))
    np.savez_compressed(
        GRAPH,
        format=np.asarray(GRAPH_FORMAT),
        edge=np.asarray(edges, dtype=np.int64),
        support=support_matrix(proper),
        tree_edge=np.asarray(edges, dtype=np.int64),
    )
    print("WROTE", ROADMAP)
    print("WROTE", GRAPH)
    print(f"SLICE REGION QUOTIENT: {len(proper)} proper support patterns")


def fraction_array(numerators, denominators):
    return tuple(
        Fraction(int(numerator), int(denominator))
        for numerator, denominator in zip(numerators, denominators)
    )


def verify():
    certificate = np.load(ROADMAP, allow_pickle=False)
    required = {
        "format",
        "parent_index",
        "source_chart",
        "varying_position",
        "segment_num",
        "segment_den",
        "box_lo_num",
        "box_lo_den",
        "box_hi_num",
        "box_hi_den",
        "sample_num",
        "sample_den",
        "wall_offset",
        "wall_fourset",
        "gcd_offset",
        "gcd_numerator",
        "gcd_denominator",
        "cell_tope",
        "signature",
        "signature_pattern",
    }
    if set(certificate.files) != required:
        raise AssertionError(f"wrong line-roadmap fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong line-roadmap format")
    if int(certificate["parent_index"].item()) != slice_verify.PARENT_INDEX:
        raise AssertionError("wrong parent index")
    if int(certificate["source_chart"].item()) != slice_verify.SOURCE_CHART:
        raise AssertionError("wrong source chart")
    if tuple(map(int, certificate["varying_position"])) != (
        slice_verify.VARYING_ROW,
        slice_verify.VARYING_COLUMN,
    ):
        raise AssertionError("wrong varying entry")
    if fraction_array(certificate["segment_num"], certificate["segment_den"]) != SEGMENT:
        raise AssertionError("wrong line segment")
    stored_boxes = tuple(
        zip(
            fraction_array(certificate["box_lo_num"], certificate["box_lo_den"]),
            fraction_array(certificate["box_hi_num"], certificate["box_hi_den"]),
        )
    )
    if stored_boxes != BOXES:
        raise AssertionError("wrong wall isolating boxes")
    if fraction_array(certificate["sample_num"], certificate["sample_den"]) != SAMPLES:
        raise AssertionError("wrong cell samples")

    base = slice_verify.source_parent()
    expected = slice_verify.expected_parent_signs()
    for endpoint in SEGMENT:
        if topes.parent_signs(slice_verify.scaled_parent(base, endpoint)) != expected:
            raise AssertionError("parent sign failure at line endpoint")
    groups, gcds = wall_groups(base)

    offsets = tuple(map(int, certificate["wall_offset"]))
    if len(offsets) != len(groups) + 1 or offsets[0] != 0:
        raise AssertionError("wrong wall offsets")
    stored_flat = tuple(tuple(map(int, row)) for row in certificate["wall_fourset"])
    stored_groups = tuple(
        stored_flat[offsets[index] : offsets[index + 1]]
        for index in range(len(groups))
    )
    if stored_groups != groups:
        raise AssertionError("stored wall occurrence groups disagree")

    gcd_offsets = tuple(map(int, certificate["gcd_offset"]))
    numerators = tuple(Fraction(int(value)) for value in certificate["gcd_numerator"])
    denominators = tuple(Fraction(int(value)) for value in certificate["gcd_denominator"])
    stored_gcds = tuple(
        tuple(
            numerators[position] / denominators[position]
            for position in range(gcd_offsets[index], gcd_offsets[index + 1])
        )
        for index in range(len(gcd_offsets) - 1)
    )
    if stored_gcds != gcds:
        raise AssertionError("stored exact wall gcds disagree")

    recomputed_topes = enumerate_cell_topes(base)
    stored_topes = tuple(tuple(map(int, row)) for row in certificate["cell_tope"])
    if stored_topes != recomputed_topes:
        raise AssertionError("stored complete cell labels disagree")
    patterns, proper = signature_patterns(stored_topes)
    verify_interval_structure(patterns)
    signatures = tuple(map(int, certificate["signature"]))
    stored_patterns = tuple(map(int, certificate["signature_pattern"]))
    if signatures != tuple(sorted(patterns)):
        raise AssertionError("stored signature union disagrees")
    if stored_patterns != tuple(patterns[signature] for signature in signatures):
        raise AssertionError("stored signature support patterns disagree")

    graph = np.load(GRAPH, allow_pickle=False)
    if set(graph.files) != {"format", "edge", "support", "tree_edge"}:
        raise AssertionError("wrong line graph fields")
    if str(graph["format"].item()) != GRAPH_FORMAT:
        raise AssertionError("wrong line graph format")
    if not np.array_equal(graph["support"], support_matrix(proper)):
        raise AssertionError("line graph region quotient disagrees")

    print("PASS: 89 labeled residual roots grouped into 25 exact crossing points")
    print("PASS: disjoint Sturm boxes cover every residual root on (-1/2,1/2)")
    print("PASS: all 26 cells have 26,112 exact supported signatures")
    print("PASS: every one of 26,232 line-supported signatures has interval support")
    print("PASS: supports are 25,992 full, plus 25 prefixes and 25 suffixes")
    print(f"PASS: complete slice region quotient has {len(proper)} proper rows")
    print("THEOREM: every finite signature-family support is connected on this line")
    print("THEOREM: certified 26-cell labeled residual roadmap inside parent 2599")
    print("SCOPE: complete on the displayed coordinate line, not the 9D parent cell")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    if args.build or args.build_only:
        build()
    if not args.build_only:
        verify()


if __name__ == "__main__":
    main()
