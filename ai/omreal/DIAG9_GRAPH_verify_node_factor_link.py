#!/usr/bin/env python3
"""Link the two exact row-2599 node branches to global factor classes."""

from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
GLOBAL = HERE / "data" / "DIAG9_GRAPH_global_factor_census.npz"
NODE = HERE / "data" / "DIAG9_GRAPH_row2599_node_roadmap.npz"
EXPECTED_FACTOR_IDS = (1657, 12874)


def rows(array):
    return tuple(tuple(map(int, row)) for row in array)


def main():
    with np.load(GLOBAL, allow_pickle=False) as source:
        global_data = {name: source[name] for name in source.files}
    with np.load(NODE, allow_pickle=False) as source:
        node_data = {name: source[name] for name in source.files}

    if str(global_data["format"].item()) != "diag9-global-residual-factor-census-v1":
        raise AssertionError("wrong global factor certificate format")
    if str(node_data["format"].item()) != "diag9-row2599-transverse-node-v1":
        raise AssertionError("wrong transverse-node certificate format")

    occurrence = rows(global_data["occurrence_fourset"])
    if len(occurrence) != 84_840 or len(set(occurrence)) != 84_840:
        raise AssertionError("global occurrence keys are not unique")
    lookup = {
        fourset: int(global_data["occurrence_factor"][index])
        for index, fourset in enumerate(occurrence)
    }
    multiplicity = tuple(map(int, global_data["factor_multiplicity"]))

    offsets = tuple(map(int, node_data["branch_offset"]))
    branch_foursets = rows(node_data["branch_fourset"])
    if offsets != (0, 65, 130):
        raise AssertionError("wrong node branch offsets")
    factor_ids = []
    for branch in range(2):
        members = branch_foursets[offsets[branch] : offsets[branch + 1]]
        if len(members) != 65 or len(set(members)) != 65:
            raise AssertionError("node branch does not have 65 distinct occurrences")
        classes = {lookup[fourset] for fourset in members}
        if len(classes) != 1:
            raise AssertionError("a local branch splits across global factors")
        factor = classes.pop()
        if multiplicity[factor] != 65:
            raise AssertionError("node branch is not its complete size-65 class")
        factor_ids.append(factor)

    if tuple(factor_ids) != EXPECTED_FACTOR_IDS:
        raise AssertionError("node global factor IDs changed")
    if len(set(factor_ids)) != 2:
        raise AssertionError("the transverse branches are one global wall")

    print("PASS: node branch 0 is exactly global factor class 1657 (size 65)")
    print("PASS: node branch 1 is exactly global factor class 12874 (size 65)")
    print("THEOREM: the exact row-2599 node crosses two distinct global walls")


if __name__ == "__main__":
    main()
