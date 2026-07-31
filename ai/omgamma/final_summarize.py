"""Assemble the final results table from all summaries on disk."""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    rows = []
    for path in sorted(glob.glob(f"{HERE}/data/flip_*_summary.json")):
        s = json.load(open(path))
        rows.append((s['n'], s['r'], s['classes'],
                     s.get('catalog_matches_bfs'),
                     s['perm_holonomy_order'] == s['S_n_order'],
                     s['H_equals_Gbar'],
                     s.get('gamma_bar_connected'),
                     s.get('gamma_tilde_connected'), 'runflip'))
    for path in sorted(glob.glob(f"{HERE}/data/big_*/summary.json")):
        s = json.load(open(path))
        rows.append((s['n'], s['r'], s['classes'],
                     s.get('complete_by_mass'),
                     s.get('gamma_tilde_connected'),
                     s['H_equals_Gbar'],
                     s.get('gamma_bar_connected'),
                     s.get('gamma_tilde_connected'), 'runbig'))
    rows.sort()
    print(f"{'(n,r)':>8} {'classes':>9} {'complete':>9} {'H=Gbar':>7} "
          f"{'bar':>5} {'tilde':>6}  src")
    for (n, r, c, comp, pi, hf, gb, gt, src) in rows:
        print(f"({n},{r})".rjust(8) + f"{c:>10} {str(comp):>9} "
              f"{str(hf):>7} {str(gb):>5} {str(gt):>6}  {src}")
    # count files
    for path in sorted(glob.glob(f"{HERE}/data/mass_target_*.json")):
        s = json.load(open(path))
        print(f"mass target ({s['r']},{s['n']}): N_chi = {s['N_chi']} "
              f"(pairs {s['N_pairs']})")


if __name__ == "__main__":
    main()
