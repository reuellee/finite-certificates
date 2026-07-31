Ancillary files for "The maximum number of vertices of a
(3,5)-zonoboxtope is 42".

Contents
--------
verify_c66_new_cases.py   Stdlib-only exact verifier (Python >= 3.10).
cert_35_42.json           The 42-vertex (3,5)-zonoboxtope of Prop. 2.
cert_38_110.json          The 110-vertex (3,8)-zonoboxtope of Prop. 3.
cert_46_104.json          The 104-vertex (4,6)-zonoboxtope of Prop. 3.
cert_45_58.json           A  58-vertex (4,5)-zonoboxtope (lower bound).
cert_37_84.json           An 84-vertex (3,7)-zonoboxtope (lower bound).

Usage
-----
    python verify_c66_new_cases.py

Runs in about 2 seconds and exits 0 with "PASS" if and only if every
instance has exactly its claimed vertex count. All arithmetic is exact
(fractions.Fraction); no third-party packages are required.

Each JSON file records the segment directions U (rows u_i), midpoints M
(rows m_i), coefficient vectors a and b, a strict witness direction for
every claimed vertex, and an explicit convex-combination certificate for
every non-vertex candidate. The verifier recomputes the 2^(n+1)
candidate sign points of Q = conv(sum_i a_i(m_i+[-u_i,u_i]) union
sum_i b_i(m_i+[-u_i,u_i])), checks they are pairwise distinct, and
checks every witness and every convex combination exactly.

The upper-bound certificate library (132,560 cell-wide Gordan
certificates), its generating programs, and the full prose account are
in the public repository

    https://github.com/reuellee/finite-certificates

under ai/maxout (see ai/maxout/capstone/CAPSTONE.md). Its independent
verifier, ai/maxout/capstone/independent_audit.py, is also stdlib-only
(about 2 minutes for the whole library) and imports nothing from the
programs that produced the certificates.
