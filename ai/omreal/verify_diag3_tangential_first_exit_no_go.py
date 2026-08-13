#!/usr/bin/env python3
"""Exact no-go for assembling pointwise first-exit rays without frontier data.

This is a small semialgebraic topology model, not a model of the 9DVL bad
loci.  It proves that acyclicity of every independently compactified
first-exit fiber does not imply that those fibers form a proper strip pair.
"""

from fractions import Fraction


def selected_strip(s, u):
    """Fiber component containing u=0 before its selected first exit."""

    if not (Fraction(-1) <= s <= Fraction(1) and Fraction(0) <= u <= 2):
        return False
    return u < (1 if s == 0 else 2)


def selected_terminal(s, u):
    # u=2 is the ambient parent boundary over the whole base, even though the
    # selected first-exit fiber at s=0 stops earlier at the triple point u=1.
    return (s == 0 and u == 1) or u == 2


def rank_q(matrix):
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (index for index in range(row, len(work)) if work[index][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        value = work[row][column]
        work[row] = [entry / value for entry in work[row]]
        for other in range(len(work)):
            if other == row or not work[other][column]:
                continue
            value = work[other][column]
            work[other] = [
                entry - value * pivot_entry
                for entry, pivot_entry in zip(work[other], work[row], strict=True)
            ]
        row += 1
    return row


def main():
    # Every rational point (1/n,3/2) is in the selected open strip, while its
    # limit (0,3/2) is feasible but neither selected nor relative.  Thus adding
    # only the pointwise terminal endpoints does not make a closed subset of
    # the compact rectangle, so projection to the base is not proper.
    limit_u = Fraction(3, 2)
    for denominator in range(1, 101):
        point_s = Fraction(1, denominator)
        if not selected_strip(point_s, limit_u):
            raise AssertionError("approaching point left the selected strip")
    if selected_strip(0, limit_u) or selected_terminal(0, limit_u):
        raise AssertionError("the nonrelative jump frontier was accidentally added")
    print("PASS selected first-exit union is nonclosed at (0,3/2)")

    # If one closes the union in the ambient rectangle, the s=0 fiber becomes
    # [0,2].  Its genuine relative subset is {1,2}: u=1 is the triple exit and
    # u=2 is parent infinity.  In the relative cellular complex with vertices
    # 1 and 2 removed, d_1(e_01)=-v_0 and d_1(e_12)=0.  Therefore H_1=Q.
    boundary_1 = ((-1, 0),)  # C1=Q^2 -> C0=Q
    h1 = 2 - rank_q(boundary_1)
    if h1 != 1:
        raise AssertionError(f"wrong closed-fiber relative H1: {h1}")
    print("PASS closure fiber H_1([0,2],{1,2};Q)=Q")
    print("NO-GO pointwise acyclic exit fibers do not imply a proper strip pair")
    print("NEEDED continuous exit/Hardt frontier or complete two-parameter atlas")


if __name__ == "__main__":
    main()
