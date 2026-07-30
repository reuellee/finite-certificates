"""Third-party exact cross-check of every certified extremal instance.

Recomputes the vertex count of each certified zonoboxtope instance with
Komei Fukuda's cddlib (via pycddlib's exact-GMP module `cdd.gmp`) — a
codebase entirely independent of this repo's verifiers, of qhull, and of
the model-generated pipelines. For each instance the full candidate set
(all sign points of both zonotopes) is passed as exact rational generators;
cddlib's redundancy removal yields the extreme-point count, which must
equal the certified f0.

Not named verify_*.py because it needs the optional pycddlib dependency
(pip install pycddlib); the repo's core verifiers remain stdlib-only.

Usage: python check_instances_cddlib.py       (~1 min, exact arithmetic)
"""
import itertools
import json
import os
import sys
from fractions import Fraction

import cdd.gmp as cg

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = [("cert_d4n4.json", 32), ("cert_35_42.json", 42),
         ("cert_45_58.json", 58), ("cert_37_84.json", 84),
         ("cert_46_104.json", 104), ("cert_38_110.json", 110)]


def points_mub(cert):
    """New-style cert: segments m_i + [-u_i, u_i], coefficients a, b."""
    M = [[Fraction(x) for x in r] for r in cert["M"]]
    U = [[Fraction(x) for x in r] for r in cert["U"]]
    a = [Fraction(x) for x in cert["a"]]
    b = [Fraction(x) for x in cert["b"]]
    n, d = len(U), len(U[0])
    pts = []
    for coef in (a, b):
        cen = [sum(coef[i] * M[i][j] for i in range(n)) for j in range(d)]
        for s in itertools.product((-1, 1), repeat=n):
            pts.append(tuple(cen[j] + sum(s[i] * coef[i] * U[i][j]
                                          for i in range(n)) for j in range(d)))
    return pts


def points_vlam(cert):
    """(4,4)-style cert: centered segments V, scalings lam."""
    V = [[Fraction(x) for x in r] for r in cert["V"]]
    lam = [Fraction(x) for x in cert["lam"]]
    n, d = len(V), len(V[0])
    pts = []
    for scale in ([Fraction(1)] * n, lam):
        for s in itertools.product((-1, 1), repeat=n):
            pts.append(tuple(sum(Fraction(s[i]) * scale[i] * V[i][j]
                                 for i in range(n)) for j in range(d)))
    return pts


def main():
    ok = True
    for fname, want in CASES:
        cert = json.load(open(os.path.join(HERE, fname)))
        pts = points_vlam(cert) if "V" in cert else points_mub(cert)
        if len(set(pts)) != len(pts):
            print(f"{fname}: FAIL (candidate points not distinct)")
            ok = False
            continue
        rows = [[1] + list(p) for p in pts]
        mat = cg.matrix_from_array(rows, rep_type=cg.RepType.GENERATOR)
        redundant = cg.redundant_rows(mat)
        got = len(pts) - len(redundant)
        status = "OK" if got == want else "MISMATCH"
        if got != want:
            ok = False
        print(f"{fname}: cddlib exact vertex count = {got} "
              f"(certified {want}) -> {status}")
    print("PASS: cddlib agrees with every certified count" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
