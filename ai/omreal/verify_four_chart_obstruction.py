#!/usr/bin/env python3
"""Exact verifier that four realization charts do not suffice at UOM(4,8).

The search that found the matrices is outside the trust boundary.  This
verifier independently enumerates the abstract extensions of parent 2599,
canonicalizes them with the coverage checker, and recomputes every bracket of
one integer realization for every resulting child class.
"""

from collections import Counter
import json
import sys

import four_chart_gate as gate


def main():
    parents = [
        line.strip() for line in gate.CATALOG_48.open(encoding="utf-8") if line.strip()
    ]
    parent = parents[gate.PARENT_INDEX]
    counts = {
        record["i"]: record
        for record in (
            json.loads(line) for line in gate.EXTCOUNTS.open(encoding="utf-8")
            if line.strip()
        )
    }
    assert counts[gate.PARENT_INDEX]["E"] == gate.EXPECTED_EXTENSIONS

    lex_core = gate.lexicographic_signatures(parent)
    assert len(lex_core) == 2_624
    four_capacity = 4 * 26_112 - 3 * len(lex_core)
    assert four_capacity == gate.FOUR_CHART_CAPACITY == 96_576

    parent_bits, signatures = gate.enumerate_extensions(parent)
    assert len(signatures) == len(set(signatures)) == gate.EXPECTED_EXTENSIONS

    # Import only the checker side.  No catalog-generator module has been
    # imported into this process, which is enforced by coverage_checker.py.
    sys.path.insert(0, str(gate.OMMINOR))
    import minorlib as ml

    extension_bits = gate.extension_bit_matrix(parent_bits, signatures)
    hi, lo, _nargmax, valid = ml.canon_keys(9, 4, extension_bits, batch=500)
    assert valid.all()
    multiplicities = Counter((int(h), int(l)) for h, l in zip(hi, lo))
    assert len(multiplicities) == gate.EXPECTED_CHILD_CLASSES == 5_902
    assert sum(multiplicities.values()) == gate.EXPECTED_EXTENSIONS
    assert Counter(multiplicities.values()) == gate.EXPECTED_MULTIPLICITIES

    certificate = gate.HERE / "data" / "seeat_parent2599_realizations.npz"
    realized = gate.verify_realization_certificate(certificate, multiplicities)
    assert set(realized) == set(multiplicities)
    realizable_signatures = sum(multiplicities[key] for key in realized)
    assert realizable_signatures == 97_224
    assert realizable_signatures > four_capacity

    print("PASS parent 2599: 97224/97224 abstract extensions realizable")
    print("PASS universal lexicographic core: 2624 signatures in every chart")
    print("PASS four-chart capacity: 4*26112 - 3*2624 = 96576")
    print("THEOREM: atlas width(parent 2599) >= 5; four-chart SEEAT is false")


if __name__ == "__main__":
    main()
