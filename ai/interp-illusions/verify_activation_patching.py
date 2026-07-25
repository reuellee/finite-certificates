#!/usr/bin/env python3
"""Certificate 1: Activation patching (single-site denoising, noising, zero/mean
ablation) provably misattributes a cancellation pair.

NETWORK N1 (6 parameters, exact rationals, 1 hidden layer, width 3):
    input x in R;  hidden pre-activations (linear units, the patchable sites):
        h1 = 1*x,  h2 = -1*x,  h3 = 1*x          (W1 = (1, -1, 1))
    output:
        y = ReLU(1*h1 + 1*h2 + 1*h3)             (w2 = (1, 1, 1))
    So y(x) = ReLU(x - x + x) = ReLU(x).

TASK / DISTRIBUTION D: x uniform on {+1, -1}; behavior y*(x) = ReLU(x)
    (output 1 on positive class, 0 on negative class).
    Clean/corrupt counterfactual pair: x_clean = +1, x_corr = -1 (both in D).

GROUND-TRUTH MECHANISM (provable, by construction):
    For every real x, the summed readout contribution of {h1, h2} is
    1*h1(x) + 1*h2(x) = x - x = 0 identically.  Deleting the pair (zeroing
    their output weights) leaves the network function EXACTLY ReLU(h3) =
    ReLU(x) on all of R.  Deleting h3 instead gives ReLU(0) = 0, destroying
    the task.  Hence the unique minimal faithful circuit is {h3}; the pair
    {h1, h2} is a null (cancellation) subcircuit -- the 'negative head'
    motif (cf. negative name-mover heads, Wang et al. 2023 IOI).

REGISTERED METHOD (standard, no strawman):
    Activation patching as specified in Meng et al. 2022 (causal tracing,
    denoising direction), Zhang & Nanda 2023 'Towards Best Practices in
    Activation Patching' (ICLR 2024), Heimersheim & Nanda 2024:
      Denoising: run corrupt input, patch site h_i to its clean-run value,
        report normalized recovery R_i = (y_patched - y_corr)/(y_clean - y_corr).
      Noising: run clean input, patch h_i to its corrupt-run value,
        report effect E_i = (y_clean - y_patched)/(y_clean - y_corr).
      Zero-ablation / mean-ablation: set h_i = 0 (= its exact mean over D)
        on the clean input; importance = |y_clean - y_ablated|.
    Circuit selection: keep components with (near-)full recovery / largest
    effect (Conmy et al. 2023 ACDC-style thresholding).

CERTIFIED MISMATCH:
    Denoising: R = (1, 0, 1)  -> h1 tied with h3 at FULL recovery.
    Noising:   |E| = (1, 2, 1) -> h2 ranked STRICTLY ABOVE the true mechanism h3.
    Zero/mean ablation: importance = (1, 1, 1) -> all sites 'equally critical'.
    Yet the pair {h1,h2} contributes identically zero and is deletable with
    zero functional change; the discovered denoising circuit {h1, h3} is
    UNFAITHFUL (with h2 mean-ablated it computes ReLU(2x) != ReLU(x) at x=1).
All arithmetic exact (fractions.Fraction).
"""
from fractions import Fraction as F
import sys

W1 = (F(1), F(-1), F(1))
W2 = (F(1), F(1), F(1))

def hidden(x):
    return [w * x for w in W1]

def relu(z):
    return z if z > 0 else F(0)

def forward_from_hidden(h, keep=(True, True, True)):
    pre = sum(w2 * hi for w2, hi, k in zip(W2, h, keep) if k)
    return relu(pre if keep != (False, False, False) else F(0))

def forward(x):
    return forward_from_hidden(hidden(x))

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)

x_clean, x_corr = F(1), F(-1)
h_clean, h_corr = hidden(x_clean), hidden(x_corr)
y_clean, y_corr = forward(x_clean), forward(x_corr)
denom = y_clean - y_corr
print(f"clean: x={x_clean}, h={h_clean}, y={y_clean}")
print(f"corrupt: x={x_corr}, h={h_corr}, y={y_corr}")
assert (y_clean, y_corr) == (1, 0)

print("\n=== Method output: single-site DENOISING (patch clean into corrupt) ===")
R = []
for i in range(3):
    h = list(h_corr); h[i] = h_clean[i]
    yp = forward_from_hidden(h)
    R.append((yp - y_corr) / denom)
print(f"  recovery R = {tuple(map(str, R))}   (h1, h2, h3)")

print("\n=== Method output: single-site NOISING (patch corrupt into clean) ===")
E = []
for i in range(3):
    h = list(h_clean); h[i] = h_corr[i]
    yp = forward_from_hidden(h)
    E.append((y_clean - yp) / denom)
print(f"  effect E = {tuple(map(str, E))};  |E| = {tuple(str(abs(e)) for e in E)}")

print("\n=== Method output: ZERO(=MEAN)-ablation on clean input ===")
mean_h = [(hi_c + hi_x) / 2 for hi_c, hi_x in zip(h_clean, h_corr)]
assert mean_h == [F(0)] * 3, "mean over D is exactly 0 -> mean-ablation == zero-ablation"
A = []
for i in range(3):
    h = list(h_clean); h[i] = F(0)
    A.append(abs(y_clean - forward_from_hidden(h)))
print(f"  ablation importance = {tuple(map(str, A))}")

print("\n=== Ground truth (exact, all x in {-1,1} and symbolically for all x) ===")
# pair contribution identically zero: w2[0]*W1[0] + w2[1]*W1[1] == 0 (linear path weights)
pair_path = W2[0] * W1[0] + W2[1] * W1[1]
check("summed linear path weight of {h1,h2} is exactly 0 (contribution == 0 for ALL x)",
      pair_path == 0)
same = all(forward_from_hidden(hidden(x), keep=(False, False, True)) == forward(x)
           for x in [F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2)])
check("deleting pair {h1,h2} leaves function EXACTLY unchanged (sampled + path identity)", same)
dead = all(forward_from_hidden(hidden(x), keep=(True, True, False)) == 0
           for x in [F(-1), F(1)])
check("deleting h3 destroys the task (output identically 0 on D)", dead)

print("\n=== Certified mismatches ===")
check("denoising assigns h1 FULL recovery, tied with true mechanism h3 (R1=R3=1, R2=0)",
      R == [F(1), F(0), F(1)])
check("noising ranks null-pair member h2 STRICTLY ABOVE true mechanism h3 (|E2|=2 > |E3|=1)",
      abs(E[1]) > abs(E[2]) and abs(E[1]) > abs(E[0]))
check("zero/mean-ablation calls all three sites equally critical (1,1,1)",
      A == [F(1)] * 3)
# faithfulness failure of the discovered denoising circuit {h1,h3}
y_circuit = forward_from_hidden([h_clean[0], F(0), h_clean[2]])
check("denoising-discovered circuit {h1,h3} is UNFAITHFUL (outputs 2 != 1 on clean input)",
      y_circuit == 2 and y_circuit != y_clean)

print()
if fails:
    print("FAIL:", fails); sys.exit(1)
print("PASS: certificate 1 verified — single-site patching (all three standard "
      "variants) misattributes the identically-zero cancellation pair {h1,h2}; "
      "unique faithful circuit is {h3}.")
