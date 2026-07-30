import json
import gzip
from fractions import Fraction
import sys
sys.path.append('stage2c_gemini')
import check_cellwide
sys.path.append('stage2b_gpt')
import check_stage2b

def main():
    bits = 516678
    k = 1
    split = [1, -1, -1, -1, -1]
    
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    
    witness = sym_cov['splits']['1']['residue_pattern_strict_primal_witnesses']['xx-xx-x++x']
    witness = [Fraction(v) for v in witness]
    
    rows = check_stage2b.symmetric_reduced_rows(check_stage2b.U_EXPECTED, bits, k)
    
    print("Primal witness x:", witness)
    print("\nSymmetric reduced rows and Bx:")
    margins = []
    for r in rows:
        margin = sum(a * b for a, b in zip(r, witness))
        margins.append(margin)
        print("Row:", r, "-> Margin:", margin)
        
    print("\nMin margin:", min(margins))
    
    # Let's map the y_values to the rows of this symmetric_reduced_rows matrix.
    # The symmetric reduced rows are ordered by the non-'x' markers in the pattern, then the 5 weight rows.
    # For xx-xx-x++x:
    # pair 2 (0,3) is '-', so it's the 1st row.
    # pair 5 (1,3) is '-', so it's the 2nd row.
    # pair 7 (2,3) is '+', so it's the 3rd row.
    # pair 8 (2,4) is '+', so it's the 4th row.
    # Then w_0..w_4 are rows 4..8.
    
    # The certificate uses (0,3,+), (0,3,-), w_1, w_2, w_4.
    # For pair 2 (0,3), y_+ = 728, y_- = 728. Since we sum the rows in the symmetric system, the multiplier for the reduced row is 728.
    
    y = [0]*len(rows)
    # pair 2 is the 0-th reduced row.
    y[0] = 728
    # weights: w_0..w_4 are rows 4..8.
    y[4 + 1] = 17886960 # w_1
    y[4 + 2] = 10352160 # w_2
    y[4 + 4] = 16361072 # w_4
    
    print("\ny vector:", y)
    
    # Check y^T (Bx):
    dot_prod = sum(y_i * m_i for y_i, m_i in zip(y, margins))
    print("y^T (Bx) =", dot_prod)
    
    # Also check y^T B = 0 directly:
    yB = [0]*8
    for i, r in enumerate(rows):
        for j in range(8):
            yB[j] += y[i] * r[j]
    print("y^T B =", yB)

if __name__ == '__main__':
    main()
