# A third-party empirical result, independently verified and replicated

**This is not our work.** "Causal-Ontology Inversion in Overcomplete Sparse
Autoencoders" was produced in a separate GPT session; what is ours is the verification.
Unlike everything else in this collection it is an *empirical* result — 120 trained
SAEs — so it cannot be settled by a finite exact certificate. It is settled instead by
independent recomputation and independent replication.

**Recomputation.** `audit_dossier.py` is self-contained: hand it the dossier and
nothing else and it extracts all 17 appendices, recomputes every registered statistic
from the raw 120-row table, reproduces the 20,000-replicate bootstrap **bit-exactly**,
and re-applies the decision rules. 87 PASS / 1 FAIL, the failure being stale hard-coded
literals at the 6th decimal in a narrative template.

**Replication.** `REPLICATION_RECORD.md` — all 120 SAEs retrained from frozen sources
on different hardware. Both primary effect sizes land within 2.4e−3 of the originals
(L1 ΔA −0.2549 vs −0.2553; TopK −0.4068 vs −0.4092), 12/12 seed signs, all gates pass,
P1/P2/P3 identical.

**Read with four disclosures**, stated in full in `IMPORT_ADJUDICATION.md`: the
preregistration has no trusted timestamp (treat as post-hoc — the one risk that cannot
be retired); it is **not byte-reproducible** even at exactly matched library versions,
because dataset construction is BLAS-dispatch dependent; the planted factors are
exactly orthogonal, so generalisation to correlated natural features is untested; and
TopK's β=0 alignment is near-ceiling.

## Verify

```
python3 audit_dossier.py EMPIRICAL_VERIFICATION_DOSSIER.md
```

Expect **86/88**, not 87/88, from this directory — the extra failure is the auditor's
own hermeticity check, invalidated by our replication's weight files existing on the
same machine. Explained in `REPLICATION_RECORD.md`.

Part of [finite-certificates](../../README.md).
