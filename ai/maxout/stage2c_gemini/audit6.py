import json
import gzip
import sympy
from fractions import Fraction
import sys
sys.path.append('stage2c_gemini')
import check_cellwide

def main():
    bits = 516678
    k = 1
    split = [1, -1, -1, -1, -1]
    
    # Check the cert for 32316 (bits = 516678, k=1)
    with open('stage2c_gemini/symbolic_certs.json', 'r') as f:
        certs = json.load(f)
        
    my_cert = next(c for c in certs if c['sigma_bits'] == 516678)
    
    # 1. verify symbolically using check_cellwide
    from sympy.parsing.sympy_parser import parse_expr
    hypotheses = {}
    for key, val_str in my_cert['multipliers'].items():
        hypotheses[key] = parse_expr(val_str, local_dict=check_cellwide.D_sym_dict)
        
    t_pass, w_pass, pos_classes = check_cellwide.verify_certificate(bits, k, my_cert['support'], hypotheses)
    print("Symbolic verification:")
    print("t_pass:", t_pass)
    print("w_pass:", w_pass)
    print("pos_classes:", pos_classes)
    
    # 2. Evaluate at U_ints
    print("\nNumeric verification at U_ints:")
    y_vals = {}
    for key, expr in hypotheses.items():
        y_vals[key] = check_cellwide.check_cellwide_eval(expr, check_cellwide.U_ints)
        print(f"y_{key} = {y_vals[key]}")
        
    # Check numeric equality
    T_eqs = [0]*5
    W_eqs = [0]*5
    
    PAIRS = list(check_cellwide.itertools.combinations(range(5), 2))
    
    for s in my_cert['support']:
        y_s = y_vals[s]
        if s.startswith('w_'):
            t = int(s[2:])
            W_eqs[t] += y_s
        else:
            i, j, sign_str = s.strip('()').split(',')
            i, j = int(i), int(j)
            pair_idx = PAIRS.index((i, j))
            
            is_plus = (sign_str == '+')
            side = 2 * pair_idx if is_plus else 2 * pair_idx + 1
            ray_orientation = 1 if is_plus else -1
            sigma_s = 1 if (bits & (1 << side)) else -1
            
            normal_scalar = sigma_s * ray_orientation
            
            for t in range(5):
                tup = tuple(sorted((t,i,j)))
                if tup[0] == tup[1] or tup[1] == tup[2]: continue
                
                det = check_cellwide.det3(check_cellwide.U_ints[t], check_cellwide.U_ints[i], check_cellwide.U_ints[j])
                
                # T equation coefficient is normal_scalar * p_var(t, i, j).
                # But wait, T equation in reference_structure uses C_ij. 
                # Let's just use check_cellwide's exact setup.
                # Actually, check_cellwide uses p_var for T eqs.
                T_eqs[t] += y_s * normal_scalar * check_cellwide.chi_dict[tup] * abs(det) # wait, p_var evaluated is chi_dict * abs(det).
                # Wait, p_var(t,i,j) evaluated is det(U_t, U_i, U_j).
                # Let's write det precisely:
                det_eval = check_cellwide.det3(check_cellwide.U_ints[t], check_cellwide.U_ints[i], check_cellwide.U_ints[j])
                
                # p_var sign:
                p_var_expr = check_cellwide.p_var(t, i, j)
                if p_var_expr != 0:
                    sign_pvar = 1 if list(p_var_expr.as_coefficients_dict().values())[0] > 0 else -1
                    # p_var is sign_pvar * p_{sorted}.
                    # The numeric value of p_var(t,i,j) is exactly det(U_t, U_i, U_j).
                    T_eqs[t] += y_s * normal_scalar * det_eval
                
                if t not in (i,j):
                    D_tij = abs(det_eval)
                    W_eqs[t] += y_s * (sigma_s * split[t]) * D_tij

    print("T_eqs evaluated:", T_eqs)
    print("W_eqs evaluated:", W_eqs)
    
if __name__ == '__main__':
    main()
