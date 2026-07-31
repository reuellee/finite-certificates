import json
import gzip

def audit():
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    
    bits_not_both = set(sym_cov['classes_not_covered_for_both_splits_bits'])
    bits_neither = set(sym_cov['classes_covered_for_neither_split_bits'])
    
    with gzip.open('stage2b_gpt/gordan_bundle.json.gz', 'rt') as f:
        bundle = json.load(f)
    
    reps = bundle['representatives']
    print(f"Number of representatives: {len(reps)}")
    
    with open('stage2c_gemini/call2_outcomes.json', 'r') as f:
        outcomes = json.load(f)
        
    call1_targets = list(outcomes.keys())
    
    residue_count = 0
    
    for t_str in call1_targets:
        t = int(t_str)
        if t < len(reps):
            system = reps[t]
            # Depending on how gordan_bundle is structured, sigma_bits might be an integer or keyed.
            if isinstance(system, dict) and 'sigma_bits' in system:
                bits = system['sigma_bits']
            elif isinstance(system, list):
                # if it's a list, we might need to know the index for bits.
                bits = system[0] # guess
            elif isinstance(system, int):
                # if reps is just a list of bits
                bits = system
            else:
                bits = system
                
            in_not_both = bits in bits_not_both
            in_neither = bits in bits_neither
            status = "neither"
            if in_neither:
                status = "both splits"
            elif in_not_both:
                status = "one split"
                
            print(f"Target idx {t}, bits {bits}, residue status: {status}")

if __name__ == '__main__':
    audit()
