#!/usr/bin/env python3
"""Certificate 4: linear probing (with the Hewitt-Liang control-task upgrade)
certifies a feature as 'encoded' in a neuron whose causal effect on the
network's output is EXACTLY zero.

NETWORK N4 (4 parameters, exact rationals):
    input x;  hidden h = (h1, h2) = (1*x, 2*x);  output y = 1*h1 + 0*h2 = x.
TASK / DISTRIBUTION D: x uniform on {-2, -1, 1, 2}; probed feature
    z(x) = sign(x)  (the class the network's output tracks: y = x, sign-aligned).

GROUND-TRUTH CAUSAL FACTS (provable — the h2 readout weight is exactly 0):
    ANY intervention on h2 (zeroing, swapping across inputs, arbitrary values)
    leaves the output y exactly unchanged on every input.  Interventions on h1
    change y one-to-one.  h1 fully mediates the behavior; h2 is causally inert.

REGISTERED METHOD (standard probing workflow):
    (a) Diagnostic classifier / probe on a component (Alain & Bengio 2016;
        Belinkov 2022 survey): fit a linear classifier from the component's
        activation to feature z; if accuracy is high, report the component
        'encodes' / 'represents' z.
    (b) Weight-based localization: min-norm least-squares probe on the full
        layer; rank neurons by |probe weight| (common neuron-attribution
        practice, cf. Dalvi et al. 2019 'What is one grain of sand...').
    (c) Control task selectivity (Hewitt & Liang 2019): selectivity =
        task accuracy - expected control-task accuracy (random labels);
        high selectivity is the registered defense against 'the probe
        memorized'.  We compute the control expectation EXACTLY by
        enumerating all 16 labelings of the 4 input types.

METHOD OUTPUT (exact):
    (a) Probe on h2 alone: 100% accuracy -> 'h2 encodes z'.
    (b) Min-norm LS probe on (h1,h2) for z: w = (3/25, 6/25); |w_h2| = 2|w_h1|
        -> weight ranking places the inert neuron FIRST.  Probe accuracy 100%.
    (c) Selectivity of the h2 probe = 1 - 7/8 = 1/8 > 0: the h2 probe
        PASSES the control-task defense.
CERTIFIED MISMATCH: the full registered pipeline (accuracy + selectivity +
    weight ranking) reports h2 as the primary carrier of z, while h2 is
    provably causally inert (readout weight exactly 0) and h1 alone mediates.
All arithmetic exact (fractions.Fraction); exit nonzero on failure.
"""
from fractions import Fraction as F
from itertools import product
import sys

XS = [F(-2), F(-1), F(1), F(2)]
def hid(x):  return (x, 2 * x)
W_OUT = (F(1), F(0))
def out(h):  return W_OUT[0] * h[0] + W_OUT[1] * h[1]
def z(x):    return 1 if x > 0 else -1

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)

print("=== Ground truth: exact causal facts ===")
inert = all(out((hid(x)[0], v)) == out(hid(x))
            for x in XS for v in [F(0), F(7), F(-3), hid(-x)[1]])
check("h2 causally inert: every intervention on h2 leaves y unchanged (w_out,2 = 0)",
      inert and W_OUT[1] == 0)
check("h1 mediates: setting h1 <- h1(x') moves y to y(x') exactly, all pairs",
      all(out((hid(xp)[0], hid(x)[1])) == out(hid(xp)) for x in XS for xp in XS))

print("\n=== (a) probe on h2 alone ===")
# 1-D linear threshold probe on h2 = 2x: threshold 0 classifies perfectly.
acc_h2 = F(sum(1 for x in XS if (1 if hid(x)[1] > 0 else -1) == z(x)), len(XS))
print(f"  accuracy of threshold-0 probe on h2: {acc_h2}")
check("probe on inert neuron h2 alone achieves 100% accuracy", acc_h2 == 1)

print("\n=== (b) min-norm least-squares probe on (h1, h2) ===")
# fit z ~ w.h ; h = (x, 2x) => w.h = c*x with c = w1 + 2*w2.
# LS over c: c* = sum(x z)/sum(x^2); min-norm w s.t. w1 + 2 w2 = c*: w = c*(1,2)/5
c_star = F(sum(x * z(x) for x in XS), sum(x * x for x in XS))
w = (c_star * F(1, 5), c_star * F(2, 5))
acc_full = F(sum(1 for x in XS
                 if (1 if w[0]*hid(x)[0] + w[1]*hid(x)[1] > 0 else -1) == z(x)), 4)
print(f"  c* = {c_star}, min-norm w = ({w[0]}, {w[1]}), probe accuracy = {acc_full}")
check("min-norm probe: |weight on inert h2| = 2 x |weight on causal h1|",
      abs(w[1]) == 2 * abs(w[0]) and w[1] != 0)
check("full-layer probe accuracy 100%", acc_full == 1)

print("\n=== (c) Hewitt-Liang control task for the h2 probe (exact enumeration) ===")
# probe family on 1-D h2: sign(a*h2 + b) => all threshold functions (10 of them
# incl. both polarities and constants) over the 4 sorted values of h2.
h2_vals = sorted(hid(x)[1] for x in XS)
def best_threshold_acc(labels):  # labels: tuple over sorted h2_vals
    best = 0
    for cut in range(5):          # predict -1 below cut, +1 at/after; both polarities
        for pol in (1, -1):
            pred = [pol * (1 if i >= cut else -1) for i in range(4)]
            best = max(best, sum(p == l for p, l in zip(pred, labels)))
    return F(best, 4)
E_control = sum(best_threshold_acc(lab) for lab in product((-1, 1), repeat=4)) / 16
selectivity = acc_h2 - E_control
print(f"  expected control accuracy = {E_control}, selectivity = {selectivity}")
check("expected control accuracy = 7/8 (exact enumeration of 16 labelings)",
      E_control == F(7, 8))
check("h2 probe selectivity = 1/8 > 0: passes the control-task defense",
      selectivity == F(1, 8) and selectivity > 0)

print("\n=== Certified mismatch ===")
check("pipeline verdict 'h2 encodes z (100% acc, selective, largest weight)' "
      "vs ground truth 'h2 causally inert, h1 mediates'",
      acc_h2 == 1 and selectivity > 0 and abs(w[1]) > abs(w[0])
      and W_OUT[1] == 0)

print()
if fails:
    print("FAIL:", fails); sys.exit(1)
print("PASS: certificate 4 verified — the registered probing pipeline (accuracy "
      "+ selectivity + weight ranking) names the causally inert neuron h2 as "
      "the primary carrier of the feature.")
