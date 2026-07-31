import json
import gzip
import subprocess
import os

def check_pattern(bits):
    # To get pattern from bits, we need to know the mapping.
    # The pattern string is 10 chars, corresponding to the 10 pairs in class order.
    # From reference_structure.json:
    with open('stage2b_gpt/reference_structure.json', 'r') as f:
        ref = json.load(f)
    
    pairs = ref['pairs_in_class_order']
    # Wait, the bits map to 20 sides. The side 0 is for +, side 1 is for -.
    # So bit 2*c is pair c, side +. bit 2*c+1 is pair c, side -.
    # Let's extract the pattern: 
    # if side + and side - have the same sign, we put '+' or '-'. If different, 'x'.
    pattern = ""
    for c in range(10):
        s_plus = (bits >> (2*c)) & 1
        s_minus = (bits >> (2*c + 1)) & 1
        if s_plus == s_minus:
            pattern += '+' if s_plus == 1 else '-'
        else:
            pattern += 'x'
    return pattern

def run_checker():
    print("Running check_cellwide.py...")
    result = subprocess.run(['python', 'stage2c_gemini/check_cellwide.py', 'stage2c_gemini/symbolic_certs.json'], capture_output=True, text=True)
    print("Return code:", result.returncode)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

def main():
    run_checker()
    
    bits = 516678
    pattern = check_pattern(bits)
    print(f"Bits {bits} -> pattern {pattern}")
    
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    
    witness = sym_cov['splits']['1']['residue_pattern_strict_primal_witnesses'].get(pattern)
    print("Witness:", witness)

if __name__ == '__main__':
    main()
