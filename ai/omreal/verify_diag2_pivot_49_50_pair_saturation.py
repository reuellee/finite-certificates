#!/usr/bin/env python3
"""Exact closure of the six type-(49,50) labeled-pair residue orbits.

`DIAG2_PIVOT_LABELED_PAIR_THEOREM.md` leaves 115 pair orbits open, six of
them of type `(49,50)`. This checker closes all six, generalizing
`verify_diag2_pivot_49_pair_saturation.py`'s elimination (there q_49's pivot
`d` has unit coefficient; here the same q_49 elimination is reused unchanged,
since every `(49,50)` pair orbit representative canonically anchors at type
49 -- 49 < 50, so `pair_orbit_representatives`'s `min(forward, reverse)`
canonicalization always picks it) to the second wall being an arbitrary
type-50 relabeled factor instead of another type-49 one.

Four of the six saturate their localized critical ideal to the unit ideal
exactly as the seven type-(49,49) cases do, giving the same "smooth
7-manifold, hence noncompact" conclusion. The other two (20097, 20112) did
not reach the unit ideal within the same bounded search budget used
throughout this repository (`processed<1000, basis<100`); both are
nonetheless closed by the strictly weaker "affine in some variable" argument
of `DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md`, which this checker also verifies
for all six as a uniform closing step.
"""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import verify_diag2_pivot_49_pair_saturation as sat49  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


ZERO_MONOMIAL = sat49.ZERO_MONOMIAL
VARS = "abcdefghi"

# The exact six (49,50)-type residue orbits, confirmed below to be exactly
# the residue reported when the existing all-frame certificate audit is
# scoped to the (49,50) factor-type candidate population.
RESIDUE_49_50 = (8218, 8387, 12366, 12371, 20097, 20112)

# target: (restricted terms, degree, affine variables found)
EXPECTED = {
    8218: (183, 8, ("e",)),
    8387: (120, 7, ("e", "h")),
    12366: (72, 6, ("a", "c", "i")),
    12371: (82, 7, ("a", "c", "g", "i")),
    20097: (183, 7, ("h",)),
    20112: (191, 8, ("e", "h")),
}

# Of the six, only these four have a full saturation attempted here (each
# takes seconds to a few minutes). The other two (20097, 20112) exhaust the
# same (processed<1000, basis<100) bounded search used throughout this
# repository WITHOUT reaching the unit ideal -- confirmed once, by hand, in
# roughly half an hour each; that is not re-run on every invocation of this
# checker, since the affine-fiber argument alone already closes them (see
# DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md) and re-exhausting a known-bounded
# search on every CI run would only spend time to reconfirm a negative.
ATTEMPT_SATURATION = {8218: True, 8387: True, 12366: True, 12371: True, 20097: False, 20112: False}

# For the four attempted: (basis size, s-pairs processed) at the unit ideal.
SATURATION_EXPECTED = {
    8218: (49, 66),
    8387: (8, 0),
    12366: (9, 0),
    12371: (9, 0),
}

# Bounded-search budget for the saturation attempt, matching
# verify_diag2_pivot_49_pair_saturation.py's own (1000, 100) exactly -- no
# extra resources were used to reach the four successes.
MAX_PROCESSED = 1000
MAX_BASIS = 100


def restricted_and_derivatives(target_polynomial):
    restricted = sat49.substitute_d(target_polynomial)
    active_variables = sat49.ACTIVE_VARIABLES
    generators = (dict(restricted),) + tuple(
        representative.derivative(restricted, variable) for variable in active_variables
    )
    return restricted, generators


def affine_variables(restricted):
    # See the matching guard/comment in
    # verify_diag2_affine_fiber_residue_closure.py: an identically-zero
    # restricted polynomial would vacuously read every variable as affine.
    if not restricted:
        raise AssertionError("degenerate (identically zero) restricted polynomial")
    return tuple(
        v
        for v in VARS
        if v != "d"
        and max((mono[VARS.index(v)] for mono in restricted), default=0) <= 1
    )


def attempt_saturation(restricted, generators, brackets):
    """Same bounded localized-Buchberger search as
    verify_diag2_pivot_49_pair_saturation.py, just returning failure instead
    of raising when the bound is exhausted (that script only ever calls it
    on cases already known to succeed)."""

    basis = []
    history = []
    for source, generator in enumerate(generators):
        reduced, labels = sat49.localized_normal_form(generator, basis, brackets)
        if not reduced:
            continue
        basis.append(reduced)
        history.append(("generator", source, labels, reduced))
        if reduced == {ZERO_MONOMIAL: 1}:
            return True, tuple(basis), tuple(history), 0

    import heapq

    queue = []
    serial = 0
    for right in range(len(basis)):
        for left in range(right):
            if sat49.relatively_prime(sat49.leading(basis[left]), sat49.leading(basis[right])):
                continue
            common = sat49.monomial_lcm(sat49.leading(basis[left]), sat49.leading(basis[right]))
            heapq.heappush(queue, (sum(common), serial, left, right))
            serial += 1
    processed = 0
    known = {sat49.signature(polynomial) for polynomial in basis}
    while queue and processed < MAX_PROCESSED and len(basis) < MAX_BASIS:
        _degree, _serial, left, right = heapq.heappop(queue)
        processed += 1
        candidate, labels = sat49.localized_normal_form(
            sat49.s_polynomial(basis[left], basis[right]), basis, brackets
        )
        if not candidate or sat49.signature(candidate) in known:
            continue
        known.add(sat49.signature(candidate))
        index = len(basis)
        basis.append(candidate)
        history.append(("spoly", left, right, labels, candidate))
        if candidate == {ZERO_MONOMIAL: 1}:
            return True, tuple(basis), tuple(history), processed
        for old in range(index):
            if sat49.relatively_prime(sat49.leading(basis[old]), sat49.leading(candidate)):
                continue
            common = sat49.monomial_lcm(sat49.leading(basis[old]), sat49.leading(candidate))
            heapq.heappush(queue, (sum(common), serial, old, index))
            serial += 1
    return False, tuple(basis), tuple(history), processed


def main():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    pair_orbits, _ordered_counts, _orbit_sizes = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    residue_pairs = tuple((49, target) for target in RESIDUE_49_50)
    if not set(residue_pairs).issubset(pair_orbits):
        raise AssertionError("the six (49,50) targets are not orbit representatives")

    audit = labeled.audit_pairs(
        residue_pairs, factor_polynomial, occurrences, occurrence_factor,
        all_frames=True, progress=False,
    )
    certified, residue = audit[:2]
    if certified or tuple(sorted(residue)) != tuple(sorted(residue_pairs)):
        raise AssertionError("the six (49,50) pairs changed under the existing certificate audit")
    print("PASS: all six (49,50) pairs independently reconfirmed unresolved by prior certificates")

    brackets = sat49.restricted_parent_brackets()
    print("PASS: restricted nonconstant parent-bracket units:", len(brackets))

    reached_count = 0
    for target in RESIDUE_49_50:
        restricted, generators = restricted_and_derivatives(factor_polynomial[target])
        degree = max(map(sum, restricted))
        affine = affine_variables(restricted)
        report = (len(restricted), degree, affine)
        if report != EXPECTED[target]:
            raise AssertionError(f"target {target} report changed: {report!r} != {EXPECTED[target]!r}")
        if not affine:
            raise AssertionError(f"target {target} has no affine-fiber closing argument")

        if ATTEMPT_SATURATION[target]:
            reached, basis, history, processed = attempt_saturation(restricted, generators, brackets)
            if not reached:
                raise AssertionError(f"target {target} was expected to reach the unit ideal")
            saturation_report = (len(basis), processed)
            if saturation_report != SATURATION_EXPECTED[target]:
                raise AssertionError(
                    f"target {target} saturation trace changed: {saturation_report!r}"
                )
            reached_count += 1
            print(
                f"PASS target={target}: terms={len(restricted)} degree={degree} "
                f"reached_unit=True basis={saturation_report[0]} "
                f"s-pairs={saturation_report[1]} affine_in={affine}"
            )
        else:
            print(
                f"PASS target={target}: terms={len(restricted)} degree={degree} "
                f"reached_unit=not-attempted affine_in={affine}"
            )

    print(f"PASS: {reached_count}/6 targets fully saturate to the unit ideal (smooth 7-manifold)")
    print("PASS: 6/6 targets close via the affine-fiber argument (noncompact)")
    print("THEOREM all six type-(49,50) pair-wall common-zero loci are noncompact")
    print("STATUS certified relative-label pair orbits: 9367/9476 (via this + prior certificates); residue: 109")
    print("CAVEAT diagonal two still requires global decorated transition-cycle acyclicity")


if __name__ == "__main__":
    main()
