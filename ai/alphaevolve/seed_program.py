"""Seed program for the AlphaEvolve campaign on Conjecture 6.6.

PROBLEM.  Fix d and n.  Choose n segments  I_i = m_i + [-u_i, u_i]  in R^d
(m_i, u_i in R^d) and two nonnegative coefficient vectors a, b in R^n.  Put

    Z^a = sum_i a_i I_i ,   Z^b = sum_i b_i I_i ,   Q = conv(Z^a u Z^b).

Q is a (d,n)-zonoboxtope.  Every vertex of Q is a sign point of Z^a or of Z^b,
so the 2^(n+1) points

    (sum_i c_i m_i) + sum_i s_i c_i u_i ,   s in {-1,1}^n,  c in {a, b}

are the only candidates, and f0(Q) = how many of them are extreme.
MAXIMISE f0.  `nverts(M, U, a, b)` computes it (M has rows m_i, U rows u_i).

TARGETS.  (d,n) = (4,5): best known 58, conjectured maximum 60, cap 60.
          (d,n) = (3,7): best known 84, conjectured maximum 88, cap 88.
Anything above 58 / 84 is a NEW RESULT.  Nothing can exceed the cap.

WHAT IS ALREADY KNOWN TO FAIL -- do not just rebuild it.
This exact family has been searched hard and the following all terminate at
58 / 84 and never move:
  * the source paper's own sampling recipe (segment endpoints drawn uniformly
    on the unit sphere, weights split 2:1 / 1:2 between an A-group and a
    B-group), at 15x the sample budget the paper reports as sufficient;
  * random restart + coordinate hill-climbing over (M, U, a, b), which is what
    the code below does -- it IS the incumbent, and it plateaus;
  * ~300 complete-per-direction-set branch-and-bound searches over side-sign
    assignments;
  * seeding by deleting one generator from the exactly certified extremal
    instances at (4,6) with 104 vertices and (3,8) with 110 vertices (all
    drops land at or below the plateau).
Meanwhile every case with n even, or with n = d, hits its conjectured maximum
within minutes of generic sampling: 16 at (3,3), 26 at (3,4), 60 at (3,6),
32 at (4,4), 104 at (4,6), 110 at (3,8).  The resistance is specific to odd
n > d.  So if a better instance exists it is NOT generic: it lives in a thin,
structured region that random sampling and local search do not reach.

WHERE TO LOOK INSTEAD.  Structure, not a better hill-climber.  Ideas worth
trying: algebraic / incommensurate direction sets (the source paper's own
extremal constructions in dimension 2 for odd n are incommensurate fans, e.g.
directions at angles that are irrational multiples of pi, or entries built
from sqrt(2), the golden ratio, roots of unity of an order coprime to n);
cyclic / symmetric configurations (moment curve, cyclic polytope directions,
regular-simplex or cross-polytope normals, orbits of a finite group acting on
R^d); exact small-integer or Pythagorean-quadruple direction sets; degenerate
limits where several candidate points nearly coincide, approached from the
side that keeps them distinct; deliberately unbalanced A/B splits and weight
ratios far from 2:1; parameterisations in which the offset vector
T = sum_A a_i m_i - sum_B b_j m_j (which carries ALL of the midpoint freedom)
is placed by design rather than by chance.

CONSTRAINTS.  Deterministic: use only the supplied `rng`.  `budget` counts
`nverts` calls; going over raises and ends the run, but every instance you
ever passed to `nverts` is remembered, so the best one still counts.  numpy is
available as np.  Return the best (M, U, a, b) you found.
"""
import numpy as np


# EVOLVE-BLOCK-START
def search(d, n, rng, nverts, budget):
    """Incumbent: paper-faithful sampling + coordinate hill-climb.  Plateaus."""
    best_v, best = -1, None
    used = [0]

    def score(M, U, a, b):
        used[0] += 1
        return nverts(M, U, a, b)

    while used[0] < budget - 1:
        # paper's Prop 6.5 seed: segment endpoints on the unit sphere,
        # residual weights split between the first k and the last n-k
        p = rng.normal(size=(n, d)); p /= np.linalg.norm(p, axis=1, keepdims=True)
        q = rng.normal(size=(n, d)); q /= np.linalg.norm(q, axis=1, keepdims=True)
        M, U = (p + q) / 2.0, (p - q) / 2.0
        k = n // 2
        al = rng.uniform(0.2, 1.0, k)
        be = rng.uniform(0.2, 1.0, n - k)
        a = np.concatenate([2 * al, be])
        b = np.concatenate([al, 2 * be])

        v = score(M, U, a, b)
        step = 0.25
        for _ in range(400):
            if used[0] >= budget - 1:
                break
            mask = rng.random(M.shape) < 0.3
            M2 = M + rng.normal(scale=step, size=M.shape) * mask
            U2 = U + rng.normal(scale=step, size=U.shape) * (rng.random(U.shape) < 0.3)
            a2 = np.maximum(a + rng.normal(scale=step, size=n) * (rng.random(n) < 0.3), 0)
            b2 = np.maximum(b + rng.normal(scale=step, size=n) * (rng.random(n) < 0.3), 0)
            v2 = score(M2, U2, a2, b2)
            if v2 >= v:
                M, U, a, b, v = M2, U2, a2, b2, v2
                step = min(step * 1.05, 0.25)
            else:
                step = max(step * 0.995, 0.01)
        if v > best_v:
            best_v, best = v, (M, U, a, b)
    return best
# EVOLVE-BLOCK-END
