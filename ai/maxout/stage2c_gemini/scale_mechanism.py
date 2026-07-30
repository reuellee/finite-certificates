import json
import gzip
import sys
sys.path.append('stage2c_gemini')
import check_cellwide

def main():
    # Write Phase B: scale the mechanism
    
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
        
    bits_not_both = set(sym_cov['classes_not_covered_for_both_splits_bits'])
    bits_neither = set(sym_cov['classes_covered_for_neither_split_bits'])
    
    with gzip.open('stage2b_gpt/gordan_bundle.json.gz', 'rt') as f:
        bundle = json.load(f)
    
    # 100 failed targets from STAGE2B.md / symbolic_gp_results.json
    with open('stage2b_gpt/symbolic_gp_results.json', 'r') as f:
        sym_results = json.load(f)
    
    failed_100_systems = set()
    for res in sym_results['results']:
        k = sum(1 for x in res['mapped_split'] if x == 1)
        failed_100_systems.add((res['mapped_sigma_bits'], k))
        
    reps = bundle['representatives']
    
    single_class_covered = []
    failed_100_covered = []
    
    k1_residue_overlap = 0
    k2_residue_overlap = 0
    both_residue_overlap = 0
    stage2b1_covered_overlap = 0
    
    def check_criterion(bits, k):
        split = [1]*k + [-1]*(5-k)
        for c in range(10):
            s_plus = 1 if (bits & (1 << (2*c))) else -1
            s_minus = 1 if (bits & (1 << (2*c + 1))) else -1
            
            if s_plus == s_minus:
                # get i, j
                pair = check_cellwide.TRIPLES[c] # wait, TRIPLES is 3-tuples. PAIRS?
                # Actually, reference_structure has PAIRS
                # Let's import it directly
                pass
                
    # PAIRS from reference_structure.json
    with open('stage2b_gpt/reference_structure.json', 'r') as f:
        ref = json.load(f)
    PAIRS = ref['pairs_in_class_order']
    
    def satisfies_criterion(bits, k):
        split = [1]*k + [-1]*(5-k)
        for c in range(10):
            s_plus = 1 if (bits & (1 << (2*c))) else -1
            s_minus = 1 if (bits & (1 << (2*c + 1))) else -1
            
            if s_plus == s_minus:
                i, j = PAIRS[c]
                valid = True
                for t in range(5):
                    if t not in (i, j):
                        if s_plus * split[t] != -1:
                            valid = False
                            break
                if valid:
                    return c, s_plus, i, j
        return None
        
    for r in reps:
        for bits in (r, r ^ ((1<<20)-1)):
            for k in (1, 2):
                res = satisfies_criterion(bits, k)
                if res:
                    single_class_covered.append((bits, k))
                    
                    if (bits, k) in failed_100_systems:
                        failed_100_covered.append((bits, k))
                        
                    in_not_both = bits in bits_not_both
                    in_neither = bits in bits_neither
                    
                    if not in_not_both:
                        # Covered by both splits in 2b-1
                        stage2b1_covered_overlap += 1
                    else:
                        if in_neither:
                            both_residue_overlap += 1
                        else:
                            # which residue?
                            # Stage 2b-1 is an equal-pair certificate.
                            pass
                            
    print(f"Total covered by single-class: {len(single_class_covered)}")
    print(f"Overlap with failed 100: {len(failed_100_covered)}")
    print(f"Overlap with Stage 2b-1 covered (both): {stage2b1_covered_overlap}")
    print(f"Overlap with both-residue: {both_residue_overlap}")
    
    out = {
        "criterion": "sigma_{ij,+} = sigma_{ij,-} AND sigma_{ij} * s_t = -1 for all 3 t not in {i,j}",
        "total_systems_covered": len(single_class_covered),
        "failed_100_covered": failed_100_covered,
        "residue_overlap": both_residue_overlap,
        "stage2b1_equal_pair_overlap": stage2b1_covered_overlap
    }
    
    with open('stage2c_gemini/family_scan.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == '__main__':
    main()
