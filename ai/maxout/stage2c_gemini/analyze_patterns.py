import json
import itertools
from fractions import Fraction
from pathlib import Path

DIR = Path("C:/Users/reuel/AppData/Local/Temp/claude/E--Projects/8f05ea6b-b743-4889-b448-362647b88861/scratchpad/finite-certificates/ai/maxout")
OUT = DIR / "stage2c_gemini"

with open(OUT / "extracted_certs.json") as f:
    data = json.load(f)
    
D_vals = data["D_vals"]
D_keys = list(D_vals.keys())
targets = data["targets"]

PAIRS = list(itertools.combinations(range(5), 2))

# Precompute monomials of degree 1 and 2
monomials = {}
for k in D_keys:
    monomials[(k,)] = D_vals[k]
    
for k1 in D_keys:
    for k2 in D_keys:
        if k1 <= k2:
            monomials[(k1, k2)] = D_vals[k1] * D_vals[k2]
            
# Binomials of degree 2 (M1 - M2)
binomials = {}
monomial_keys = list(monomials.keys())
for i in range(len(monomial_keys)):
    for j in range(i+1, len(monomial_keys)):
        k1 = monomial_keys[i]
        k2 = monomial_keys[j]
        if len(k1) == 2 and len(k2) == 2: # Only degree 2 binomials
            val = monomials[k1] - monomials[k2]
            if val > 0:
                binomials[(k1, "-", k2)] = val
            elif val < 0:
                binomials[(k2, "-", k1)] = -val

all_shapes = {}
monomials_and_binomials = {**monomials, **binomials}

out_txt = open(OUT / "analysis_output_utf8.txt", "w", encoding="utf-8")
def my_print(s=""): out_txt.write(s + "\n")

for t in targets:
    cert = t["cert"]
    # cert is a list of [row, val]
    support_size = len(cert)
    
    rows_desc = []
    y_vals = {}
    for row, val in cert:
        if row < 20:
            c_i = row // 2
            side = "+" if row % 2 == 0 else "-"
            pair = PAIRS[c_i]
            desc = f"({pair[0]},{pair[1]},{side})"
        else:
            t_idx = row - 20
            desc = f"w_{t_idx}"
        rows_desc.append(desc)
        y_vals[desc] = val
        
    my_print(f"Target idx={t['idx']}, source={t['source']}, rank={t.get('rank', 'N/A')}, k={t['k']}, support={support_size}")
    my_print(f"  Rows: {', '.join(rows_desc)}")
    
    # Try to find a single multiplier to normalize against, e.g. the first side row
    side_rows = [desc for desc in rows_desc if not desc.startswith("w")]
    if not side_rows:
        continue
        
    ref_row = side_rows[0]
    ref_val = y_vals[ref_row]
    
    my_print(f"  Multiplier ratio matches (ref={ref_row}):")
    matched_all = True
    for desc in rows_desc:
        if desc == ref_row:
            continue
        val = y_vals[desc]
        ratio = Fraction(val, ref_val)
        
        # Find if ratio == M1 / M2
        found_match = None
        for m1, v1 in monomials_and_binomials.items():
            for m2, v2 in monomials.items(): # restrict denominator to monomial for simplicity
                if Fraction(v1, v2) == ratio:
                    found_match = f"{m1} / {m2}"
                    break
            if found_match:
                break
        
        if found_match:
            my_print(f"    {desc} / {ref_row} = {ratio} => {found_match}")
        else:
            my_print(f"    {desc} / {ref_row} = {ratio} => NO SIMPLE MATCH")
            matched_all = False
            
    shape_key = tuple(rows_desc)
    if shape_key not in all_shapes:
        all_shapes[shape_key] = {"count": 0, "sources": set(), "matched_all": matched_all}
    all_shapes[shape_key]["count"] += 1
    all_shapes[shape_key]["sources"].add(t["source"])
    my_print()

my_print("Shapes summary:")
for shape, info in all_shapes.items():
    my_print(f"Shape: {shape} (Count: {info['count']}, Sources: {info['sources']}, MatchedAll: {info['matched_all']})")
out_txt.close()
