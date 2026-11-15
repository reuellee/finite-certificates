# Astra consultation: exact moving-corner boundary path

Base tree: local 803c98fb611fb4dfe1f9493be1714d28f1caa09f, tree identical to published 050bdb12c158df5f846a94f1426b8926d399a639. Ledger 2/9, unchanged.

Astra proposed moving the [1367]/[2467] corner while introducing the second root shear. For the authenticated row-2599 matrix, use canonical ungauged columns and perform, in order,

    c7 <- c7 + a E d; c6 <- c6 + b e1;
    c2 <- c2 - r c8; c1 <- c1 - q c2,

where a=WITNESS_WALL+TANGENT_ADVANCE, E=ENDPOINT, d=EXPECTED_DIRECTION. Solve [2467]=0 for r=R(b), and then [1367]=0 for q=Q(b). At b0=OFFPLANE_ENDPOINT, Q=0 and R=ROOT_TARGET. Q is strictly increasing on b>=0, and Q(25)<ROOT_ENDPOINTS[1]<Q(26), giving a unique b* in (25,26). The endpoint is approximately b*=25.8188188194, R=0.0836451903.

The exact executable verify_moving_corner.py rebuilds both rational functions and verifies all 70 parent determinants by exact real-root isolation on the conservative interval [b0,26]. Two walls [1367] and [2467] vanish throughout. Every other wall has the original sign on [b0,b*), and [1358] reaches zero at b*. All five signed cofactor weights for block 1 support (2,9,27,30,35), after reversing their common sign, are strictly positive throughout, and their kernel equation is checked. It also checks input digest and exact canonical starting parameters. These are exact 1D calculations, conditional on existing source/signature definitions and usual Gordan interpretation. At b0 the existing literal stored c2 is positively rescaled, so this is equality in canonical coordinates; literal gauge and witness gluing must still be proved during assembly. Astra reviewed the proof and independently checked three rational points using integer-arithmetic determinant and cofactor routines; this is not an independent full-interval verifier or external mathematical refereeing.

An earlier constant shear on the literal stored matrices fails on stages 2–4 because of their positive c2 gauges; see check_literal_shear.py. Correcting the gauge by d=[2358]>0, n=[1358], and c1'=d c1 - s n c2 forces [1358]=0 at s=1, but the fixed-collar ramp crosses to the wrong side of [1367], exactly at stage 1, t=0, s=1/4. check_gauge_ramp.py proves this and independent_corner.py recomputes that one determinant via permutation expansion.

An exploratory two-dimensional candidate solves [1367]=0 for the column-6 displacement as a rational function of r,q, then interpolates r from ROOT0 to R(b) with q=Q(b). A rational grid with b=2,10,25 and interpolation parameter 0,1/4,1/2,3/4,1 exhibited no wrong parent signs. This is a numerical/exact-point screen only: it does not establish a surface sign certificate, witness positivity, boundary identifications, or complete coverage.

Run from repository root:

    python ops/research-team/experiments/2026-11-14-d3-astra-advice/verify_moving_corner.py
    python ops/research-team/experiments/2026-11-14-d3-astra-advice/check_gauge_ramp.py
    python ops/research-team/experiments/2026-11-14-d3-astra-advice/independent_corner.py
    python ops/research-team/experiments/2026-11-14-d3-astra-advice/check_literal_shear.py
    python ops/research-team/experiments/2026-11-14-d3-astra-advice/screen_surface.py

Next gate: build and exactly certify a two-parameter wall surface including its entire boundary and positive block-1 witness, then construct the literal compatible 3D H1 prism. The moving corner alone is not that prism; H0, J, global transfer, and 3/9 remain open. No new theorem-ledger or 4/6 local comparison credit is claimed.
