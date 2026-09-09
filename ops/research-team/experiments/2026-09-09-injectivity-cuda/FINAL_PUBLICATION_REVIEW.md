# Final publication integration review

**Verdict: ACCEPT THE ADDITIVE EVIDENCE CHECKPOINT.** Clean archive replay passed
all three independent mathematical gates. The original theorem ledger remains
**2/9**, original injectivity is open, and zero original obligations are closed.
This review does not assert that remote GitHub CI has completed.

The reviewer inspected `replay_checkpoint.py`, `EVIDENCE_MANIFEST.json`, the
frozen ZIP, the dedicated workflow, the experiment README and the root README
pointer. The wrapper was run once from the publication directory and returned
`PASS_CHECKPOINT`:

- 121 archive members passed complete member accounting, byte-length checks and
  SHA256 verification. Duplicate and unsafe archive paths are rejected before
  extraction. The frozen archive contains no temporary CLI test directories,
  base64 transfer copies or Python cache files.
- All 14 visible report, review, code, instruction and certificate copies are
  byte-identical to their authenticated archive members.
- The injectivity replay returned `PASS_AUXILIARY_AND_ABSTRACT_ONLY`.
- The collision replay returned `PASS_INDEPENDENT_ABSTRACT_ONLY`.
- The actual-parent replay returned `ACCEPT_FINITE_LOCAL_CERTIFICATES_ONLY`,
  verifying 32 selected parents, 81 BAD and 15 GOOD block certificates, and 101
  exact local three-row circuit witnesses.
- Final output retains ledger `2/9` and reports GPU execution as `UNTESTED`.

The wrapper extracts into a temporary directory and runs the three independent
checkers there. It checks their expected verdicts and the final original-theorem
scope. The mathematical replay entrypoints use only the Python standard library.
The dedicated GitHub workflow registers this entrypoint for the experiment's PR
paths and research-branch pushes with read-only repository permissions. Its use
of `replay_checkpoint.py` is consistent with a separate explicit gate, without
adding an unregistered `verify_*.py` entry to the existing verifier census.
No existing workflow is changed by the submitted new workflow file.

The experiment README correctly distinguishes numerical screening from exact
acceptance and explicitly leaves CUDA execution, GPU speedup, CPU/GPU numerical
parity and Windows execution untested. The root README pointer calls these
informational local results and preserves the stated 2/9 ledger. Historical
root-README claims were not re-audited in this bounded integration review.
The baseline README was independently bound to Git blob
`e80cb94704ee991cdb2fc244c2d8b879bf72403b` at the supplied main base
`9e77c365b266e9d884e6ac14a0443992bec92c64`. A literal diff confirms that the
candidate only adds six lines: the informational pointer and its paragraph
spacing. All pre-existing README bytes are preserved in order.

Reviewed SHA256 values:

| File | SHA256 |
|---|---|
| `EVIDENCE.zip` | `db8887166c152b3fe4fa9c37a3038e64014c6e2d2cd6821071267ad942677285` |
| `EVIDENCE_MANIFEST.json` | `22e438d814650beaf3f180d2f04547587dd3735d2c06f60060d5da3d553c70ea` |
| `replay_checkpoint.py` | `d90a4437b2379a401206f3f74cf42e02529c897ac077fa135769c9f142d1356f` |
| Dedicated `injectivity-pilot.yml` | `d00e22e06f7bbe9683df3e8d8fa46f13b336ddcd3de5729dc034077be6e75283` |
| Experiment `README.md` | `4f0446af7e7d8c1b62387a89e7fdf437f511575f32bc4a8cb2c35b9fedcda5bb` |
| Root `README.md` | `29e2be1068c4dbfd1bac1f25ff8bc86c5d3dc30d969afa0422e03ec651720315` |

The archive is a complete evidence snapshot for these replay gates, not a backup
of the repository's full Git history. Remote publication integrity, CI status
and backup verification remain coordinator responsibilities.
