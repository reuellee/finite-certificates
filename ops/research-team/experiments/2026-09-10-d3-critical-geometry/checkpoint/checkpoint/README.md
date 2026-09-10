# 9DVL: pair-wall proof cycle

This is an additive continuation of the common-weak-excision checkpoint at
`401602fe9f8bcfad74116b46bb5574f63b6a3040`. The user asked us to continue
toward a third original diagonal after the usage limit reset.

Read `REPORT.md` and `CLAIM_LEDGER.json` for the final reviewed status.
The original problem counts diagonals, not auxiliary wall orbits. A completed
pair-wall endpoint alone is not an original diagonal.

`original/` contains the constructive proofs and finite applicability checks.
`alternative/` contains the alternative-route audit and the next triple target.
`falsifier/` and `newfalsifier/` contain independent challenges and exact examples.
`referee/` contains independent deductive reviews and computational replays.
`checkpoint/` preserves the complete authenticated predecessor; it is input,
not new theorem credit. `inputs/` contains additional pinned historical sources.

Run `python3 replay_checkpoint.py` to authenticate the snapshot and replay the
new exact checks in an isolated temporary copy. This verifies the computational
claims and file identities; the global proofs are conventional mathematics
reviewed by separate research agents, not proof-assistant certificates.
