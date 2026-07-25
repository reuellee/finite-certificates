#!/usr/bin/env python3
"""Certificate 3: SAE-based circuit discovery — feature absorption as an exact
circuit-level illusion.  Builds on the eps* absorption framework of the
sae-identifiability repo (theory/verify_absorption_theory.py): here we take the
strict-hierarchy regime eps = 0 (< eps*), where the ABSORBED dictionary is
loss-optimal, and push the illusion through to the induced CIRCUIT.

MODEL (exact, 2-dim activation space):
    Ground-truth features: parent a_p = e1, child a_c = e2, orthonormal.
    Data distribution D over activations x:
        joint  x = (1,1)  w.p. q = 1/2   (parent AND child present)
        psolo  x = (1,0)  w.p. p = 1/2   (parent only)
      (child never occurs alone: strict hierarchy, eps = 0.)
    Downstream behavior: linear readout  y = e1 . x  (= parent indicator).

GROUND-TRUTH MECHANISM (provable): y depends on the parent feature only.
    Erasing the child component (x -> x - (e2.x) e2) leaves y EXACTLY unchanged
    on every input; erasing the parent component sends y from 1 to 0 on every
    input.  The child feature is causally inert for y.

SAE (standard: 2 latents, unit-norm decoder columns, nonnegative codes,
    L1 penalty lam = 1/10; per-sample loss min_{f>=0} ||x - Uf||^2 + lam*1'f):
    Faithful dictionary  U_F = [e1, e2]
    Absorbed dictionary  U_A = [e1, (e1+e2)/sqrt(2)]
    We verify EXACTLY (sympy, KKT sufficiency for the convex code problem):
      (i)  optimal codes under U_A:  joint -> f = (0, sqrt(2) - lam/2)
                                     psolo -> f = (1 - lam/2, 0)
      (ii) L(U_F) - L(U_A) = q*((2 - sqrt2)*lam - lam^2/4) > 0:
           the absorbed SAE has STRICTLY lower loss (matches the repo's
           closed forms with eps = 0 < eps*), so no loss-minimizing SAE is
           the faithful dictionary.
      (iii) numeric grid scan over ALL unit-norm 2-latent dictionaries
           (angle grid) confirming none beats U_A beyond tolerance (support
           for global optimality; the pairwise claim (ii) is the exact part).

REGISTERED PIPELINE (Sparse Feature Circuits, Marks et al. 2024; standard SAE
    circuit workflow, cf. Cunningham et al. 2023):
    1. Train SAE on activations (here: use the loss-optimal dictionary).
    2. Splice: x_hat = U f(x); metric m = e1 . x_hat.
    3. Indirect effect of latent j: IE_j = f_j(x) * (e1 . u_j)  (for a linear
       readout, attribution patching and latent zero-ablation coincide exactly).
    4. Keep latents with IE above threshold -> circuit; label latents by their
       activation pattern (max-correlation / auto-interp step).

METHOD OUTPUT (exact, on joint inputs — the child-present half of D):
    IE_1 = 0 exactly (parent latent is silent: full absorption).
    IE_2 = 1 - lam*sqrt(2)/4  (~0.965): the ENTIRE circuit is latent 2.
    Labeling: latent 2 fires exactly iff the child feature is present
    (activity pattern over D: joint=1, psolo=0 = child indicator); latent 1
    fires exactly iff child is ABSENT.  No latent tracks the parent feature.
    => Pipeline's circuit claim: "on child-present inputs, y is mediated by
       the child latent; the parent latent contributes exactly 0."

CERTIFIED MISMATCH: the true mechanism reads the parent feature only and the
    child feature is causally inert, yet the loss-optimal SAE pipeline outputs
    a circuit consisting solely of the child-indicator latent and assigns the
    parent-feature latent exactly zero.  Two mechanism descriptions in the
    same CDX equivalence class (feature-basis vs absorbed-basis); the SAE
    loss provably selects the one that misattributes the computation.
"""
import sys
import numpy as np
from sympy import sqrt, Rational, Matrix, simplify, symbols, nsimplify

R = Rational
lam = R(1, 10)
q = p = R(1, 2)
s2 = sqrt(2)

U_F = Matrix([[1, 0], [0, 1]])
U_A = Matrix([[1, 1 / s2], [0, 1 / s2]])
X = {'joint': Matrix([1, 1]), 'psolo': Matrix([1, 0])}
weights = {'joint': q, 'psolo': p}

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)

def loss(x, U, f):
    r = x - U * f
    return simplify((r.T * r)[0] + lam * (f[0] + f[1]))

def kkt_ok(x, U, f):
    """Exact KKT sufficiency for min ||x-Uf||^2 + lam 1'f, f>=0 (convex)."""
    ok = True
    for j in range(2):
        gj = simplify((2 * U[:, j].T * (U * f - x))[0] + lam)
        if f[j] > 0:
            ok &= simplify(gj) == 0
        else:
            ok &= (gj >= 0) == True
        ok &= (f[j] >= 0) == True
    return ok

print("=== (i) exact optimal codes (KKT-certified) ===")
f_A_joint = Matrix([0, s2 - lam / 2])
f_A_psolo = Matrix([1 - lam / 2, 0])
f_F_joint = Matrix([1 - lam / 2, 1 - lam / 2])
f_F_psolo = Matrix([1 - lam / 2, 0])
check("U_A joint code (0, sqrt2 - lam/2) satisfies exact KKT (parent latent SILENT)",
      kkt_ok(X['joint'], U_A, f_A_joint))
check("U_A psolo code (1 - lam/2, 0) satisfies exact KKT",
      kkt_ok(X['psolo'], U_A, f_A_psolo))
check("U_F joint code satisfies exact KKT", kkt_ok(X['joint'], U_F, f_F_joint))
check("U_F psolo code satisfies exact KKT", kkt_ok(X['psolo'], U_F, f_F_psolo))

print("\n=== (ii) absorbed SAE strictly beats faithful SAE (exact) ===")
L_F = q * loss(X['joint'], U_F, f_F_joint) + p * loss(X['psolo'], U_F, f_F_psolo)
L_A = q * loss(X['joint'], U_A, f_A_joint) + p * loss(X['psolo'], U_A, f_A_psolo)
gap = simplify(L_F - L_A)
claimed_gap = q * ((2 - s2) * lam - lam**2 / 4)
print(f"  L_F = {simplify(L_F)}   L_A = {simplify(L_A)}")
print(f"  L_F - L_A = {gap}  (claimed {simplify(claimed_gap)})")
check("gap matches repo closed form q*((2-sqrt2)lam - lam^2/4)",
      simplify(gap - claimed_gap) == 0)
check("gap is strictly positive (absorbed wins; eps=0 < eps*)", (gap > 0) == True)

print("\n=== (iii) numeric grid scan over all unit-norm dictionaries ===")
def pop_loss_num(t1, t2, lam_v):
    U = np.array([[np.cos(t1), np.cos(t2)], [np.sin(t1), np.sin(t2)]])
    tot = 0.0
    for w, x in [(0.5, np.array([1., 1.])), (0.5, np.array([1., 0.]))]:
        best = x @ x
        for act in [(0,), (1,), (0, 1)]:
            Ua = U[:, list(act)]
            try:
                fv = np.linalg.solve(Ua.T @ Ua, Ua.T @ x - lam_v / 2)
            except np.linalg.LinAlgError:
                continue
            if (fv >= -1e-12).all():
                r = x - Ua @ fv
                best = min(best, r @ r + lam_v * fv.sum())
        tot += w * best
    return tot

lam_v = float(lam)
ts = np.linspace(0, np.pi, 721)
gmin = min(pop_loss_num(t1, t2, lam_v) for t1 in ts for t2 in ts if t2 > t1)
L_A_num = float(L_A)
print(f"  grid min = {gmin:.8f}   L(U_A) = {L_A_num:.8f}")
check("no dictionary on a 0.25-degree grid beats U_A by more than 1e-6 "
      "(numeric support for global optimality; exact claim is pairwise (ii))",
      gmin > L_A_num - 1e-6)

print("\n=== Method output: sparse-feature-circuit on the absorbed (optimal) SAE ===")
e1 = Matrix([1, 0])
IE = [simplify(f_A_joint[j] * (e1.T * U_A[:, j])[0]) for j in range(2)]
print(f"  on joint (child-present) inputs: IE_1 = {IE[0]},  IE_2 = {IE[1]} "
      f"(= 1 - lam*sqrt2/4 = {simplify(1 - lam*s2/4)})")
check("IE of parent latent is EXACTLY 0 on all child-present inputs", IE[0] == 0)
check("IE of latent 2 is nonzero -> discovered circuit = {latent 2} alone",
      (IE[1] > 0) == True and simplify(IE[1] - (1 - lam * s2 / 4)) == 0)
# labeling step: activation patterns over D
act = {ev: [ (f[0] > 0) == True, (f[1] > 0) == True ]
       for ev, f in [('joint', f_A_joint), ('psolo', f_A_psolo)]}
child_present = {'joint': True, 'psolo': False}
check("latent 2 activity == child-feature indicator on ALL of D (auto-interp "
      "labels it 'child'); latent 1 fires iff child ABSENT; no latent tracks parent",
      all(act[ev][1] == child_present[ev] for ev in X)
      and all(act[ev][0] == (not child_present[ev]) for ev in X))

print("\n=== Ground truth (model-space interventions, exact) ===")
y = lambda x: (e1.T * x)[0]
check("erasing CHILD component never changes y (child causally inert): "
      "y(1,1)=y(1,0)=1", y(X['joint']) == y(Matrix([1, 0])) == 1)
check("erasing PARENT component destroys y on every input",
      y(Matrix([0, 1])) == 0 and y(Matrix([0, 0])) == 0)

print()
if fails:
    print("FAIL:", fails); sys.exit(1)
print("PASS: certificate 3 verified — the loss-optimal (absorbed) SAE's circuit "
      "for the behavior on child-present inputs is exactly {child-indicator "
      "latent}, with the parent latent at exactly 0, while the true mechanism "
      "uses only the parent feature and the child feature is causally inert.")
