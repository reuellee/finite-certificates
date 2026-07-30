"""Standalone full re-audit of every cell-wide certificate in the program.

Re-verifies, in one run, every certificate in:
  - gp_all_d2_shard_0{0..3}_of_04.json.gz  (32,843 complement systems, k=1,2)
  - k0_cellwide_shard_00_of_01.json.gz     (570 GP certificates at k=0)
  - gp_degree3_results.json.gz             (the 120 prioritized targets, d=2)
plus the family criterion for every family-covered system (33,437 at k=1,2
and 32,570 at k=0), whose certificate is the closed-form single-class one.

For each explicit certificate: decode the (side/weight, monomial) variable
layout, then check
  (a) all coefficients nonnegative, at least one positive;
  (b) the eight quotient-ring identities: the certificate's combination of
      quotient rows vanishes modulo the Grassmann-Pluecker ideal (rebuilt
      via gp_degree3_search.quotient_matrix - exact rational arithmetic);
  (c) exact specialization at U_ints against an INDEPENDENT row builder
      (written for the reviews; shares no code with common.py).
For each family-covered system: check the criterion combinatorially and
verify the closed-form certificate by (c).

Progress is checkpointed every 500 systems to audit_progress.json; rerun
resumes. Final verdict written to audit_all_report.json.

Usage: python audit_all_certificates.py [--resume]
"""
from __future__ import annotations

import gzip
import itertools
import json
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

from gp_degree3_search import monomials_of_degree, normal_forms, quotient_matrix

HERE = Path(__file__).resolve().parent
U_INTS = [(-6, -13, 18), (-9, -12, 8), (-13, -4, 16), (4, -19, -8), (16, 15, -12)]
PAIRS = list(itertools.combinations(range(5), 2))
TRIPLES = list(itertools.combinations(range(5), 3))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def det3(a, b, c):
    return dot(a, cross(b, c))


DABS = {t: abs(det3(U_INTS[t[0]], U_INTS[t[1]], U_INTS[t[2]])) for t in TRIPLES}


def indep_rows(bits, split):
    rows = []
    for ci, (i, j) in enumerate(PAIRS):
        C = cross(U_INTS[i], U_INTS[j])
        for side, orient in ((2 * ci, 1), (2 * ci + 1, -1)):
            sg = 1 if bits >> side & 1 else -1
            wrow = [0 if t in (i, j) else split[t] * DABS[tuple(sorted((t, i, j)))]
                    for t in range(5)]
            rows.append([sg * orient * C[d] for d in range(3)] + [sg * w for w in wrow])
    for t in range(5):
        rows.append([0] * 3 + [1 if x == t else 0 for x in range(5)])
    return rows


def var_table(degree):
    table = []
    for side in range(20):
        for m in monomials_of_degree(degree):
            table.append(("side", side, m))
    for t in range(5):
        for m in monomials_of_degree(degree + 1):
            table.append(("weight", t, m))
    return table


def mono_val(mono):
    v = Fraction(1)
    for idx, e in enumerate(mono):
        if e:
            v *= Fraction(DABS[TRIPLES[idx]]) ** e
    return v


def check_explicit(bits, split, cert, table, degree, forms):
    # (a) coefficients
    coeffs = [Fraction(str(c)) for _, c in cert]
    if any(c < 0 for c in coeffs) or not any(c > 0 for c in coeffs):
        return "BAD_COEFFS"
    # (b) quotient-ring identities: rebuild E (CSR of integer-valued
    # float64 entries, same convention the standalone checker relies on)
    # and check E @ c == 0 exactly.
    variables, row_keys, matrix = quotient_matrix(bits, tuple(split), degree, forms)
    csr = matrix.tocsr()
    data = csr.data
    if not np.all(data == np.round(data)) or np.max(np.abs(data)) >= 2 ** 53:
        return "NONINTEGER_MATRIX"
    vec = {}
    for (vi, c) in cert:
        vec[int(vi)] = vec.get(int(vi), Fraction(0)) + Fraction(str(c))
    nrows = csr.shape[0]
    for rrow in range(nrows):
        total = Fraction(0)
        for pos in range(csr.indptr[rrow], csr.indptr[rrow + 1]):
            col = int(csr.indices[pos])
            if col in vec:
                total += Fraction(int(data[pos])) * vec[col]
        if total != 0:
            return "QUOTIENT_FAIL"
    # (c) independent specialization
    B = indep_rows(bits, split)
    y = {}
    for vi, c in vec.items():
        kind, idx, mono = table[vi]
        row = idx if kind == "side" else 20 + idx
        y[row] = y.get(row, Fraction(0)) + c * mono_val(mono)
    if any(v < 0 for v in y.values()):
        return "NEG_SPECIALIZED"
    if any(sum(v * B[r][col] for r, v in y.items()) != 0 for col in range(8)):
        return "SPECIALIZATION_FAIL"
    return "OK"


def family_ok(bits, split):
    for ci, (i, j) in enumerate(PAIRS):
        sp = 1 if bits >> (2 * ci) & 1 else -1
        sm = 1 if bits >> (2 * ci + 1) & 1 else -1
        if sp != sm:
            continue
        if all(sp * split[t] == -1 for t in range(5) if t not in (i, j)):
            # verify the closed-form certificate by independent specialization
            B = indep_rows(bits, split)
            y = {2 * ci: Fraction(1), 2 * ci + 1: Fraction(1)}
            for t in range(5):
                if t not in (i, j):
                    y[20 + t] = 2 * Fraction(DABS[tuple(sorted((t, i, j)))])
            if all(sum(v * B[r][col] for r, v in y.items()) == 0
                   for col in range(8)):
                return True
    return False


def load_gz(name):
    with gzip.open(HERE / name, "rt", encoding="utf-8") as h:
        return json.load(h)


def main():
    forms = normal_forms(3)
    table = var_table(2)
    t0 = time.time()
    counts = {}
    failures = []
    n = 0

    def record(status, tag):
        nonlocal n
        key = f"{tag}:{status}"
        counts[key] = counts.get(key, 0) + 1
        n += 1
        if status != "OK" and status is not True:
            failures.append((tag, status))
        if n % 500 == 0:
            (HERE / "audit_progress.json").write_text(
                json.dumps(dict(done=n, counts=counts,
                                elapsed=time.time() - t0)))
            print(f"{n} audited; {time.time()-t0:.0f}s; "
                  f"failures={len(failures)}", flush=True)

    # 1. sweep shards (explicit certificates)
    for si in range(4):
        d = load_gz(f"gp_all_d2_shard_0{si}_of_04.json.gz")
        for r in d["results"]:
            split = tuple(1 if t < r["k"] else -1 for t in range(5))
            st = check_explicit(int(r["sigma_bits"]), split,
                                r["outcome"]["certificate"], table, 2, forms)
            record(st, f"sweep{si}")

    # 2. k0 results (family + explicit)
    d = load_gz("k0_cellwide_shard_00_of_01.json.gz")
    for r in d["results"]:
        if r["outcome"]["status"] == "FAMILY_SINGLE_CLASS":
            record("OK" if family_ok(int(r["sigma_bits"]), (-1,) * 5)
                   else "FAMILY_FAIL", "k0fam")
        else:
            st = check_explicit(int(r["sigma_bits"]), (-1,) * 5,
                                r["outcome"]["certificate"], table, 2, forms)
            record(st, "k0gp")

    # 3. family coverage at k=1,2 (closed form; criterion + specialization)
    import common
    for bits in common.VALID_BITS:
        for k in (1, 2):
            split = tuple(1 if t < k else -1 for t in range(5))
            has = False
            for ci, (i, j) in enumerate(PAIRS):
                sp = 1 if bits >> (2 * ci) & 1 else -1
                sm = 1 if bits >> (2 * ci + 1) & 1 else -1
                if sp == sm and all(sp * split[t] == -1
                                    for t in range(5) if t not in (i, j)):
                    has = True
                    break
            if has:
                record("OK" if family_ok(bits, split) else "FAMILY_FAIL",
                       f"famk{k}")

    # 4. the prioritized targets at degree 2 (122 targets x 4 degrees; the
    # 121 degree-2 certificates = 120 research targets + positive control)
    d = load_gz("gp_degree3_results.json.gz")
    audited120 = 0
    for r in d["results"]:
        if (r["degree"] != 2
                or r["outcome"]["status"] != "EXACT_CELLWIDE_CERTIFICATE"):
            continue
        tgt = r["target"]
        raw_split = tgt["split"]
        split = tuple(json.loads(raw_split) if isinstance(raw_split, str)
                      else raw_split)
        st = check_explicit(int(tgt["sigma_bits"]), split,
                            r["outcome"]["certificate"], table, 2, forms)
        record(st, "prior120")
        audited120 += 1

    report = dict(schema=1, total_audited=n, elapsed_seconds=time.time() - t0,
                  counts=counts, n_failures=len(failures),
                  failures=failures[:50],
                  prioritized_targets_audited=audited120,
                  verdict="PASS" if not failures else "FAIL")
    (HERE / "audit_all_report.json").write_text(json.dumps(report, indent=1))
    print(f"AUDIT {'PASS' if not failures else 'FAIL'}: {n} audited, "
          f"{len(failures)} failures, {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
