"""Exact check of the GENERIC_SINGLE_CLASS family from symbolic_certs.json.

Instantiates the family on criterion-satisfying systems (sigma bits, k) using the
trusted integral row builder from stage2b_gpt/check_stage2b.py, and tests the two
weight-multiplier normalizations:
  factor 1:  y_wt = D_{t1t2t3} * D_{tij}   (as serialized in symbolic_certs.json)
  factor 2:  y_wt = 2 * D_{t1t2t3} * D_{tij}
Exact integer arithmetic only. Run from the working directory:
  E:/Projects/sae-identifiability/.venv/Scripts/python.exe stage2c_gemini/check_generic_factor2.py
"""
import gzip
import json
import sys

sys.path.append('stage2b_gpt')
import check_stage2b as c2b


def main():
    U = c2b.U_EXPECTED
    dmap = c2b.determinant_table(U)
    with gzip.open('stage2b_gpt/gordan_bundle.json.gz', 'rt') as f:
        reps = json.load(f)['representatives']

    def satisfies(bits, k):
        split = [1] * k + [-1] * (5 - k)
        for c in range(10):
            sp = 1 if bits & (1 << (2 * c)) else -1
            sm = 1 if bits & (1 << (2 * c + 1)) else -1
            if sp == sm:
                i, j = c2b.PAIRS[c]
                if all(sp * split[t] == -1 for t in range(5) if t not in (i, j)):
                    return c, sp, i, j
        return None

    tested = 0
    results = {1: 0, 2: 0}
    for r in reps:
        if tested >= 25:
            break
        for bits in (r, r ^ ((1 << 20) - 1)):
            for k in (1, 2):
                hit = satisfies(bits, k)
                if hit is None:
                    continue
                c, sigma, i, j = hit
                ts = [t for t in range(5) if t not in (i, j)]
                # abs determinant of the complementary triple ts
                P = abs(c2b.det3(U[ts[0]], U[ts[1]], U[ts[2]]))
                B = c2b.system_rows(c2b.unsigned_side_rows(U, k), bits)
                for factor in (1, 2):
                    y = [0] * 25
                    y[2 * c] = P
                    y[2 * c + 1] = P
                    for t in ts:
                        y[20 + t] = factor * P * dmap[(t, i, j)]
                    totals = [sum(y[row] * B[row][col] for row in range(25))
                              for col in range(8)]
                    ok = totals == [0] * 8 and any(y) and all(v >= 0 for v in y)
                    if ok:
                        results[factor] += 1
                tested += 1
                if tested >= 25:
                    break
            if tested >= 25:
                break
    print(f"systems tested: {tested}")
    print(f"factor 1 (as serialized) valid: {results[1]}/{tested}")
    print(f"factor 2 valid:                {results[2]}/{tested}")
    if results[2] == tested and results[1] == 0:
        print("VERDICT: generic family is CORRECT with factor 2 on weight rows; "
              "serialized entry (factor 1) is off by 2 and does NOT satisfy B^T y = 0.")
    elif results[1] == tested:
        print("VERDICT: serialized entry (factor 1) is correct as written.")
    else:
        print("VERDICT: mixed/unexpected — inspect conventions.")


if __name__ == '__main__':
    main()
