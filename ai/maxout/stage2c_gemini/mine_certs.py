import json
import gzip
import random
from pathlib import Path
from fractions import Fraction
import numpy as np

random.seed(2026073010)

DIR = Path("C:/Users/reuel/AppData/Local/Temp/claude/E--Projects/8f05ea6b-b743-4889-b448-362647b88861/scratchpad/finite-certificates/ai/maxout")
S2B = DIR / "stage2b_gpt"
OUT = DIR / "stage2c_gemini"
OUT.mkdir(exist_ok=True)

# 1. Load U_ints and compute exact determinants
def det3(a, b, c):
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1]) -
        a[1] * (b[0] * c[2] - b[2] * c[0]) +
        a[2] * (b[0] * c[1] - b[1] * c[0])
    )

with open(S2B / "reference_structure.json") as f:
    ref = json.load(f)
U_ints = ref["U_ints"]
reps = ref["global_flip_representatives"]  # 16570 of them
reps_sorted = sorted(reps)

D = {}
for i in range(5):
    for j in range(i+1, 5):
        for k in range(j+1, 5):
            D[(i,j,k)] = abs(det3(U_ints[i], U_ints[j], U_ints[k]))

# 2. Pick 12 from symbolic_gp_results.json
with open(S2B / "symbolic_gp_results.json") as f:
    sym = json.load(f)

failed_sym = [x for x in sym["results"] if not x["symbolic_certificate_found"]]
sel_sym = random.sample(failed_sym, 12)

# 3. Pick 12 from symmetric_coverage.json.gz
with gzip.open(S2B / "symmetric_coverage.json.gz", "rt", encoding="utf-8") as f:
    sym_cov = json.load(f)

both_residue = sym_cov["classes_not_covered_for_both_splits_bits"]
sel_sym_cov = random.sample(both_residue, 12)

# Find positions in bundle
def get_bundle_index(sigma_bits, k):
    # k can be 1, 2, 3, 4
    # If k=3, 4, map to k=2, 1 and flip sigma
    if k in (3, 4):
        k_map = 2 if k == 3 else 1
        sigma_map = sigma_bits ^ ((1 << 20) - 1)
    else:
        k_map = k
        sigma_map = sigma_bits
    
    if sigma_map in reps_sorted:
        rep = sigma_map
        is_flipped = False
    else:
        rep = sigma_map ^ ((1 << 20) - 1)
        is_flipped = True
        
    rep_idx = reps_sorted.index(rep)
    
    # Bundle order:
    # for rep in reps_sorted:
    #   for sigma in (rep, rep xor (2^20-1)):
    #     for k in (1, 2):
    return rep_idx * 4 + (2 if is_flipped else 0) + (k_map - 1)

targets = []

for t in sel_sym:
    sigma = t["mapped_sigma_bits"]
    k = sum(1 for x in t["mapped_split"] if x == 1)
    idx = get_bundle_index(sigma, k)
    targets.append({"source": "symbolic_gp", "sigma": sigma, "k": k, "idx": idx, "rank": t["rank"]})

for t in sel_sym_cov:
    # t is a representative bit mask
    # For symmetric residue, let's pick k=1 and k=2 for the rep
    sigma = t
    k = 1 # pick k=1
    idx = get_bundle_index(sigma, k)
    targets.append({"source": "symmetric_cov", "sigma": sigma, "k": k, "idx": idx})
    
target_indices = {t["idx"]: t for t in targets}

# 4. Extract certificates
extracted = []
with gzip.open(S2B / "gordan_bundle.json.gz", "rt", encoding="utf-8") as f:
    bundle = json.load(f)
    certs = bundle["certificates"]
    for idx, t in target_indices.items():
        t["cert"] = certs[idx]
        extracted.append(t)

with open(OUT / "extracted_certs.json", "w") as f:
    json.dump({"D": ["D{}{}{}".format(i,j,k) for (i,j,k) in D.keys()], "D_vals": {f"D{i}{j}{k}": v for (i,j,k), v in D.items()}, "targets": extracted}, f, indent=2)

print("Extracted", len(extracted), "certificates")
