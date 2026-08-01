# Draft email to the authors of *Maxout Polytopes* — NOT SENT, AND NOT TO BE

**Decision, 2026-08-01 (repository owner): do not send.** The repository is
maintained as a portfolio demonstrating the research quality obtainable by
directing AI systems, not as a bid for priority in the oriented-matroid or
maxout-polytope literature. Contacting the authors is therefore out of
scope. The draft is retained as a record of the decision and of what such
a message would have contained, should that judgement ever change.

---


Recipients: Andrei Balakin, Shelby Cox, Georg Loho, Bernd Sturmfels
(addresses to be looked up from their institutional pages; do not guess).

Send only after the arXiv note is posted, so the message can cite it — a
preprint link makes this a normal scholarly communication rather than an
unverifiable claim in an inbox. Keep it short; the verifier is the argument.

---

**Subject:** A counterexample to the tightness of Prop. 6.5 at n=5, and to
Conjecture 6.6.1 (odd case) — with an exact certificate

Dear Professor Sturmfels, Dr Loho, Dr Cox, Mr Balakin,

I have been working computationally on Conjecture 6.6 of *Maxout
Polytopes* (arXiv:2509.21286), and I believe I have settled the first
open odd case in the negative. I would rather tell you before it
circulates than after.

**The claim.** The maximum number of vertices of a (3,5)-zonoboxtope is
42, not 44. Consequently the tightness assertion of Proposition 6.5 fails
at n = 5, and part 1 of Conjecture 6.6 fails at its first instance beyond
n = 3. The upper bound rests on 132,560 exact Gordan certificates,
covering every valid side pattern at every split-orbit representative
after a symmetry reduction to a single oriented-matroid cell; 42 is
attained by an explicit rational instance.

**The fastest way to disbelieve me.** The attainment takes two seconds:
the ancillary files of the note include the instance and a Python
standard-library verifier that proves, in exact rational arithmetic, that
it has exactly 42 vertices. The upper bound takes about two minutes, via
a from-scratch checker that imports nothing from the programs that
generated the certificates.

Preprint: [arXiv link]
Repository: https://github.com/reuellee/finite-certificates (ai/maxout)

**Where I think the discrepancy comes from.** My implementation
reproduces the other three values of Proposition 6.5 (16, 26, 60) and
certifies exact instances attaining the conjectured values at (3,8) and
(4,6). That makes a definitional mismatch unlikely and suggests instead a
floating-point vertex-count artifact in the verification of the sampled
n = 5 example — near-duplicate vertices or a triangulated flat face would
do it. If you still have that instance, I would very much like to check
it: equipped with vertex witnesses by any exact hull code, it would take
seconds, and if it really has 44 vertices then my theorem is false and I
would want to know that immediately.

**What I am not claiming.** Only n = 5 is settled. At (4,5) and (3,7) I
have certified instances at 58 and 84 against your conjectured 60 and 88,
but those are lower bounds; whether the maxima there fall short remains
open, and I have no opinion on the general conjecture.

I should say plainly that this work was carried out by AI systems
directing exact computation under my direction, with adversarial review
between models; the note discloses this. I mention it not as a
disclaimer but because it is the reason every claim ships with a
certificate a referee can check without trusting the process that
produced it.

I would welcome any correction, and of course any collaboration or
comment you would like reflected before this goes further.

With thanks for a beautiful paper,

Reuel Lee
reuellee@gmail.com

---

## A second, separate message (only if you want it)

The oriented-matroid note is unrelated to their paper and should not be
bundled here. If it is sent at all, its natural recipients are Kolja
Knauer and Tilen Marc, and its content is: their suspected labelled
counterexample does not exist below n = 10; their Table 1 has a typo at
(9,3) (482 should be 4382); and the rank-4, n=9 class count is 9,276,595,
which agrees with their table against Fukuda–Miyata–Moriyama's
9,276,601. Same discipline applies: send after posting, lead with the
checker, claim only what is certified.
