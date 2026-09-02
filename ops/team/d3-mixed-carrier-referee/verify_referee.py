#!/usr/bin/env python3
"""Independent fail-closed referee for the frozen D3 mixed-carrier package.

This verifier deliberately does not import producer acceptance code.  It reads
the named Git objects directly, checks byte pins and contract relations with
Python's standard library, reconstructs the finite shape count and the finite
sink-SCC equivalence, and pins the bounded v1-to-v2 protocol-label repair.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[3]
BRANCH = "research/lane-d3-mixed-carrier-referee-20260901"
CYCLE_ID = "2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1"
CYCLE_DIR = f"ops/research-team/cycles/{CYCLE_ID}"
REFEREE_DIR = "ops/team/d3-mixed-carrier-referee"

CANONICAL = "9116771ba80ed3d033516d0dd666b34348aad348"
CANONICAL_TREE = "a64438426dc792af67d5ccc0dd2f4d1231dbaa14"
OPENING = "dd86907bebbfaaac9caee4e1d93dc77bc9f3ad8b"
OPENING_TREE = "a59d740c008ae04accf200a8373d16b4d9c70ae4"
INTEGRATED = "2cf92fa094b80b89816feceaf6cce6c712f72115"
INTEGRATED_TREE = "ec92c870ff48949b1c6587556b6a930e025da733"
CHECKPOINT = "f1f955f6ae69e6a847ea8795724c77896636c547"
CHECKPOINT_TREE = "c4b68a4dfdafccb66f4c69695d733fa78e840570"
PREFLIGHT = "7f135917f7ef859ec272ac3126725db272ff3ea1"
PREFLIGHT_TREE = "ab724829b045fd9a5d3f89573757db40adec6f38"
FROZEN = "2fc366e517c3bf30419b335053bec0895519b675"
FROZEN_TREE = "1520090d7f6a9ce6febeef4a0c50b31982ace560"

OPEN_VECTOR = [
    "2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
    "UNKNOWN", "UNKNOWN", 5, 8,
]
CLOSE_VECTOR = [
    "2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
    "UNKNOWN", "UNKNOWN", 6, 9,
]
OBLIGATIONS = [
    "global_gluing",
    "extension_labels",
    "strict_closure",
    "relative_infinity",
    "middle_rank_replay",
    "diag3_pair_hc1",
    "diag3_triple_hc0",
]
SOURCE_SEMANTIC_SHA256 = (
    "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
)

EXPECTED_OBJECTS = {
    "canonical": {
        "commit": CANONICAL,
        "tree": CANONICAL_TREE,
        "parents": ["fa9787b8295fae46a262d610698e7d21790c63bd"],
    },
    "opening": {
        "commit": OPENING,
        "tree": OPENING_TREE,
        "parents": [CANONICAL],
    },
    "integrated_topology": {
        "commit": "3c78fb8a181dca98b191db68395cfad9bc68f6c0",
        "tree": "418e214e7867d79d992ce50a9b8ea85c4c70fc03",
        "parents": [OPENING],
    },
    "integrated_falsifier": {
        "commit": "91e6a0eac369c93de6b8d7abee7a758c26c6aec6",
        "tree": "71b84ef98b6a969637872cafff9d60f2e33a8355",
        "parents": ["3c78fb8a181dca98b191db68395cfad9bc68f6c0"],
    },
    "integrated_evidence": {
        "commit": INTEGRATED,
        "tree": INTEGRATED_TREE,
        "parents": ["91e6a0eac369c93de6b8d7abee7a758c26c6aec6"],
    },
    "checkpoint": {
        "commit": CHECKPOINT,
        "tree": CHECKPOINT_TREE,
        "parents": [INTEGRATED],
    },
    "preflight_candidate": {
        "commit": PREFLIGHT,
        "tree": PREFLIGHT_TREE,
        "parents": [CHECKPOINT],
    },
    "candidate": {
        "commit": FROZEN,
        "tree": FROZEN_TREE,
        "parents": [PREFLIGHT],
    },
    "isolated_topology": {
        "commit": "2697c7a87c085ed6066c9903cb224518737492db",
        "tree": "418e214e7867d79d992ce50a9b8ea85c4c70fc03",
        "parents": [OPENING],
    },
    "isolated_falsifier": {
        "commit": "2c12eb03e86cf5412a9d701adafd30bcc5facb10",
        "tree": "74388045eaa5215413122143d8e45f8f2ea46f6b",
        "parents": [OPENING],
    },
    "isolated_naturality": {
        "commit": "a10a6e517af0ca66c5454926e7e7035358071c9c",
        "tree": "2418ec86497a0271820d299016357936c96ab384",
        "parents": [OPENING],
    },
}

PACKAGE_PINS = {
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json": (
        19049, "e356d00108e46be82937b18146ca47039d506ea378d489dc392d7a2ee3f865e4"
    ),
    "ai/omreal/verify_canonical_research_state_v8.py": (
        46560, "65c64767a92185a6d60f60babc02466573936363db6b985478e510ecc89f2cd7"
    ),
    "ops/research-team/PROTOCOL.md": (
        11222, "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"
    ),
    "ops/research-team/verify_cycle_protocol.py": (
        14615, "e3c2f64b97d53f4de00be675a789a42668835bb1dd8759779be8392760131753"
    ),
    f"{CYCLE_DIR}/CYCLE.md": (
        24101, "f7fcb36b2a734ae89188ae347eb332b59a0169aaefbccf07702619760371ba81"
    ),
    f"{CYCLE_DIR}/OPENING_STATE.json": (
        19899, "778d638d83f04a8beecbc400bb6ffc268698b694a8d2647e3da91ff5e8bb74d0"
    ),
    f"{CYCLE_DIR}/WORK_ORDERS.yaml": (
        7708, "88b01a3371422c28ae44c7a1dd520cd189fa09e28d707d66aace2a94b93a606b"
    ),
    f"{CYCLE_DIR}/verify_opening_state.py": (
        34040, "ff676252c6db59cb1377463679a6fe79953bdf57fd79458f34875f4435d6e01c"
    ),
    f"{CYCLE_DIR}/MID_CYCLE_CHECKPOINT.json": (
        6477, "ecc8a903955fc99286592444923372eb38e397b2bdb76cc20f0477b3e81f67cc"
    ),
    f"{CYCLE_DIR}/CLOSING_CANDIDATE.json": (
        9202, "135328356b754f97ae631bee441ae8d3c0be5ddbd0ab427bfaac344244da94fc"
    ),
    f"{CYCLE_DIR}/CYCLE_REPORT.md": (
        9862, "1e4552ab5334f12785018d3971b2ea2f4faa192e6b2081f95efffbc3a52e4f9e"
    ),
    "ops/team/d3-mixed-carrier-topology/RESULT.json": (
        18496, "7e54007c1bb97be457cbdc039c5520267cd39e39e08a930828b42708443a99e5"
    ),
    "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md": (
        11362, "131ec929171abf633b18e4eefbd1b45ec8aeea97b9d2d1a6f89a73cb205b7f76"
    ),
    "ops/team/d3-mixed-carrier-falsifier/RESULT.json": (
        7574, "89f54c80234dd74f763b390a1da86de2359a99684e3920e57cec284e6fd08480"
    ),
    "ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md": (
        15113, "de7e1d5c2758786852cbb1cf684f3af8cbf44ab4df124c7053b60534b1317936"
    ),
    "ops/team/d3-mixed-carrier-naturality/RESULT.json": (
        10798, "2911e7478a31090582dda2aeeb5e952ab84cf83946bcd5f29d3900813309e3e0"
    ),
    "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md": (
        13465, "a24821526bd0e89a1473e887d60c6e38c9e28f8d65c6a86e7f5e0d3a5d2cdb86"
    ),
}

V8_SOURCE_PINS = {
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V7.json":
        "4c5c75eaea78d005a664c61f43c2bb7559c890664e55fc2a947c4cc7e8811bcc",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CYCLE_REPORT.md":
        "ccb34a1b416bd65920a0b50f780e66292eece697847afe8042b4d7a2fd6a0df0",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CLOSING_MANIFEST.json":
        "2ef455643cc1a20812ea76a57ec650d6b251b522049851913aeedc7bcffccaea",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CLOSING_CANDIDATE.json":
        "5ff3c82930918daea52436fdcc7ab1c6da720bd913b8973dee714507df7de128",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/OBLIGATION_GRAPH.json":
        "61327b143f339cfa99620f4b3ddd3218ba86d705b87c0fdda7e81da782ad3de1",
    "ops/team/theorem-reset-prover-strategy/RESULT.json":
        "bab28affb8a72d1ff86ed86a3bad9f0f9a41dd216826e4dca8889ca5e911eafb",
    "ops/team/theorem-reset-prover-strategy/FINDINGS.md":
        "4ce7b6504cb07f75779660f0a7d04681a7e98bb5d0a72e3fb9b2884267ace9b1",
    "ops/team/theorem-reset-closing-referee/RESULT.json":
        "4e20d66ee618df991fad56230484f21251515efd9673b84c1effb98662361a3a",
    "ops/team/theorem-reset-closing-referee/REVIEW.md":
        "582d67504f9421e5f96f30585dc94fb0fd5a4df68be443331bb09153a6c150eb",
    "ops/team/theorem-reset-closing-referee/CLEAN_REPLAY.json":
        "b1394e5e7b3e5b636eed689fa07036049215a79f144e9863414e992b66776f91",
}

OPENING_SOURCE_PINS = [
    {"path": "ops/research-team/PROTOCOL.md", "bytes": 11222,
     "sha256": "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"},
    {"path": "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CLOSING_MANIFEST.json", "bytes": 4187,
     "sha256": "2ef455643cc1a20812ea76a57ec650d6b251b522049851913aeedc7bcffccaea"},
    {"path": "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CYCLE_REPORT.md", "bytes": 10862,
     "sha256": "ccb34a1b416bd65920a0b50f780e66292eece697847afe8042b4d7a2fd6a0df0"},
    {"path": "ops/team/theorem-reset-prover-strategy/FINDINGS.md", "bytes": 10081,
     "sha256": "4ce7b6504cb07f75779660f0a7d04681a7e98bb5d0a72e3fb9b2884267ace9b1"},
    {"path": "ops/team/theorem-reset-falsifier/FINDINGS.md", "bytes": 6659,
     "sha256": "893ecc8d530e7af0970cc4bb232fb34e99cb8fc5e0e6b073c93d423c7313420f"},
    {"path": "ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md", "bytes": 16265,
     "sha256": "20aafd28f9624ca595a44e3124934baa4d33b942b6c8eca6bff210fedb114c8a"},
    {"path": "ai/omreal/verify_diag3_joined_flow_triangle.py", "bytes": 9283,
     "sha256": "ac01851b53d4bed1c859f74bad2e71a5025825fe7accdac13263f5d6518a0944"},
    {"path": "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md", "bytes": 13943,
     "sha256": "141da1b6d9fcd4f601e79871aaa5d06cb98721ece928a0d0d5af83518bddf71f"},
    {"path": "ai/omreal/verify_diag3_single_bad_two_skeleton.py", "bytes": 7350,
     "sha256": "0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4"},
    {"path": "ai/omreal/DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md", "bytes": 12448,
     "sha256": "046dc84c138cbbed9add0946392d72ddb3b73b332ddb4c9029ea54348a85562e"},
    {"path": "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md", "bytes": 7170,
     "sha256": "0a372197a49f4a767c06b23a6df830ef2784e7fe653b4b3eb1a506eec0518e27"},
    {"path": "ai/omreal/NINE_DIAGONAL_STATUS.md", "bytes": 135472,
     "sha256": "07c146e835f6a62c29ab653d353d73469df1e6022018ffec76f6775b65ca7ae2"},
    {"path": "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json", "bytes": 90677,
     "sha256": "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e"},
]

EVIDENCE_PINS = {
    "ops/team/d3-mixed-carrier-topology/RESULT.json":
        "7e54007c1bb97be457cbdc039c5520267cd39e39e08a930828b42708443a99e5",
    "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md":
        "131ec929171abf633b18e4eefbd1b45ec8aeea97b9d2d1a6f89a73cb205b7f76",
    "ops/team/d3-mixed-carrier-falsifier/RESULT.json":
        "89f54c80234dd74f763b390a1da86de2359a99684e3920e57cec284e6fd08480",
    "ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md":
        "de7e1d5c2758786852cbb1cf684f3af8cbf44ab4df124c7053b60534b1317936",
    "ops/team/d3-mixed-carrier-naturality/RESULT.json":
        "2911e7478a31090582dda2aeeb5e952ab84cf83946bcd5f29d3900813309e3e0",
    "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md":
        "a24821526bd0e89a1473e887d60c6e38c9e28f8d65c6a86e7f5e0d3a5d2cdb86",
}

REQUIRED_REPORT_PHRASES = [
    "## Mandatory solution-convergence verdict",
    "Opening proof-distance vector",
    "Closing proof-distance vector",
    "Trajectory classification",
    "Automatic strategy-reset result",
    "Same-route continuation justified",
]
PROTOCOL_PASS_CLAIM = (
    "| research-cycle protocol | `PASS`, 19 cycles and 78 work orders |"
)
REPAIR_BLOCK = """## Mandatory solution-convergence verdict

Opening proof-distance vector:
`(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7, UNKNOWN, UNKNOWN, 5, 8)`.

Closing proof-distance vector:
`(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7, UNKNOWN, UNKNOWN, 6, 9)`.

Trajectory classification: **`STALLED`**. The dependency frontier is sharper,
but no load-bearing obligation or certified residual decreased.

Automatic strategy-reset result: **`STOP`**. The bounded feasibility pivot
returned three `NULL` handoffs, no full-scope negative, and no eligible
successor.

Same-route continuation justified: **`NO`**. Reopening requires a new governed
cycle with a concrete finite route for one first missing global edge.

"""


class AuditError(AssertionError):
    """A fail-closed contract violation."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    process = subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if check and process.returncode != 0:
        detail = (process.stderr or process.stdout).decode("utf-8", "replace").strip()
        raise AuditError(f"git {' '.join(args)} failed: {detail}")
    return process


def git_text(args: list[str]) -> str:
    return run_git(args).stdout.decode("utf-8", "strict").strip()


def git_bytes(commit: str, path: str) -> bytes:
    return run_git(["show", f"{commit}:{path}"]).stdout


def object_fact(commit: str) -> dict[str, Any]:
    raw = git_text(["show", "-s", "--format=%H%x00%T%x00%P", commit])
    actual_commit, tree, parents = raw.split("\x00")
    return {
        "commit": actual_commit,
        "tree": tree,
        "parents": parents.split() if parents else [],
    }


def document(raw: dict[str, bytes], path: str) -> dict[str, Any]:
    value = json.loads(raw[path].decode("utf-8"))
    require(isinstance(value, dict), f"{path}: top level is not an object")
    return value


def load_state() -> dict[str, Any]:
    raw = {path: git_bytes(FROZEN, path) for path in PACKAGE_PINS}
    return {
        "raw": raw,
        "objects": {
            role: object_fact(expected["commit"])
            for role, expected in EXPECTED_OBJECTS.items()
        },
        "docs": {
            "v8": document(raw, "ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json"),
            "opening": document(raw, f"{CYCLE_DIR}/OPENING_STATE.json"),
            "checkpoint": document(raw, f"{CYCLE_DIR}/MID_CYCLE_CHECKPOINT.json"),
            "candidate": document(raw, f"{CYCLE_DIR}/CLOSING_CANDIDATE.json"),
            "topology": document(raw, "ops/team/d3-mixed-carrier-topology/RESULT.json"),
            "falsifier": document(raw, "ops/team/d3-mixed-carrier-falsifier/RESULT.json"),
            "naturality": document(raw, "ops/team/d3-mixed-carrier-naturality/RESULT.json"),
        },
        "texts": {
            "report": raw[f"{CYCLE_DIR}/CYCLE_REPORT.md"].decode("utf-8"),
            "charter": raw[f"{CYCLE_DIR}/CYCLE.md"].decode("utf-8"),
            "work_orders": raw[f"{CYCLE_DIR}/WORK_ORDERS.yaml"].decode("utf-8"),
            "topology_memo": raw["ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md"].decode("utf-8"),
            "falsifier_memo": raw["ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md"].decode("utf-8"),
            "naturality_memo": raw["ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md"].decode("utf-8"),
        },
    }


def reconstruct_shapes() -> tuple[int, int]:
    shape_orbits = 0
    labeled_placements = 0
    for active_count in range(1, 4):
        maximum_local_sum = 3 - (active_count - 1)
        for values in itertools.product(
            range(maximum_local_sum + 1), repeat=active_count
        ):
            if sum(values) > maximum_local_sum:
                continue
            if tuple(sorted(values, reverse=True)) != values:
                continue
            shape_orbits += 1
            distinct_orders = len(set(itertools.permutations(values)))
            labeled_placements += math.comb(3, active_count) * distinct_orders
    return shape_orbits, labeled_placements


def exit_predicate_equivalence_cases() -> int:
    """Exhaust all directed graphs on three vertices and all infinity marks."""
    vertex_count = 3
    all_edges = [(u, v) for u in range(vertex_count) for v in range(vertex_count)]
    checked = 0
    for edge_mask in range(1 << len(all_edges)):
        edges = {
            edge for bit, edge in enumerate(all_edges) if edge_mask & (1 << bit)
        }
        reach = [[u == v for v in range(vertex_count)] for u in range(vertex_count)]
        for u, v in edges:
            reach[u][v] = True
        for k in range(vertex_count):
            for u in range(vertex_count):
                for v in range(vertex_count):
                    reach[u][v] = reach[u][v] or (reach[u][k] and reach[k][v])

        unseen = set(range(vertex_count))
        components: list[set[int]] = []
        while unseen:
            seed = min(unseen)
            component = {
                v for v in unseen if reach[seed][v] and reach[v][seed]
            }
            components.append(component)
            unseen -= component
        sink_components = [
            component
            for component in components
            if not any(
                u in component and v not in component for (u, v) in edges
            )
        ]
        for infinity_mask in range(1 << vertex_count):
            infinity = {
                v for v in range(vertex_count) if infinity_mask & (1 << v)
            }
            every_vertex_reaches = all(
                any(reach[u][v] for v in infinity) for u in range(vertex_count)
            )
            every_sink_contains = all(
                bool(component & infinity) for component in sink_components
            )
            require(
                every_vertex_reaches == every_sink_contains,
                "finite exit predicate is not equivalent to the sink-SCC predicate",
            )
            checked += 1
    return checked


def validate_contract(state: dict[str, Any]) -> None:
    for path, (expected_bytes, expected_sha) in PACKAGE_PINS.items():
        payload = state["raw"][path]
        require(len(payload) == expected_bytes, f"moved byte count: {path}")
        require(sha256(payload) == expected_sha, f"moved byte digest: {path}")
    require(state["objects"] == EXPECTED_OBJECTS, "Git object or parent-history drift")

    docs = state["docs"]
    v8 = docs["v8"]
    opening = docs["opening"]
    checkpoint = docs["checkpoint"]
    candidate = docs["candidate"]
    topology = docs["topology"]
    falsifier = docs["falsifier"]
    naturality = docs["naturality"]

    require(v8["format"] == "9dvl-canonical-research-state-v8", "V8 format")
    require(v8["status"] == "PIVOT_REQUIRED", "V8 status")
    require(v8["repository"]["canonical_close_commit"] == CANONICAL, "V8 close commit")
    require(v8["repository"]["canonical_close_tree"] == CANONICAL_TREE, "V8 close tree")
    require(v8["theorem"]["score"] == "2/9", "V8 ledger")
    close = v8["theorem_reset_close"]
    require(close["trajectory"] == "STALLED", "V8 trajectory")
    require(close["strategy_action"] == "STOP", "V8 action")
    require(close["overall_handoff"] == "NULL", "V8 handoff")
    require(close["selected_successor"] == "NONE", "V8 successor")
    require(close["closing_vector"] == OPEN_VECTOR, "V8 predecessor close vector")
    v8_canary = close["row2599_chart0_canary"]
    require(v8_canary["rank_d1"] == 3 and v8_canary["rank_d2"] == 6, "V8 canary ranks")
    require(v8_canary["rank_C2"] == 7, "V8 canary C2")
    require(v8_canary["primitive_h2_relation"] == [-1, 1, 1, 1, 1, 1, 1], "V8 canary relation")
    require(v8_canary["genuine_mixed_block_carrier_nonexistence_proved"] is False, "V8 canary overclaim")
    require(v8["open_obligations"]["pair_residual"] == "UNKNOWN", "V8 pair residual")
    require(v8["open_obligations"]["pair_coverage"] == "UNKNOWN", "V8 pair coverage")
    require(v8["source_pins"] == V8_SOURCE_PINS, "V8 source pins")

    require(opening["format"] == "d3-mixed-carrier-theorem-feasibility-opening-v1", "opening format")
    require(opening["cycle_id"] == CYCLE_ID, "opening cycle")
    require(opening["canonical_base"] == {
        "commit": CANONICAL,
        "tree": CANONICAL_TREE,
        "subject": "research: close theorem-level strategy reset",
        "immutable": True,
    }, "opening immutable base")
    require(opening["canonical_opening"]["ledger"] == "2/9", "opening ledger")
    require(opening["strategy_evaluation"]["construction_ready"] is False, "opening construction")
    domain = opening["selected_target"]["domain"]
    require(domain["active_block_range"] == [1, 3], "opening active range")
    require(domain["shape_quotient"] == "MODULO_ACTIVE_BLOCK_PERMUTATION_WITH_ALL_LABELED_INSTANCES_COVERED", "opening labeled shape scope")
    require(opening["selected_target"]["target_b"]["all_labeled_instances_required"] is True, "opening labeled instances")
    opening_canary = opening["opening_facts"]["flow_triangle_canary"]
    require(opening_canary["scope"] == "EXACT_LOCAL_ROW2599_CHART_ZERO_ONLY", "opening canary scope")
    require(opening_canary["primitive_generator"] == [-1, 1, 1, 1, 1, 1, 1], "opening canary relation")
    triple_open = opening["opening_facts"]["triple_only_accounting"]
    require((triple_open["settled"], triple_open["total"], triple_open["residual"]) == (77940147, 79102449, 1162302), "opening triple counts")
    require(opening["proof_distance"]["opening_vector"] == OPEN_VECTOR, "opening vector")
    require(opening["proof_distance"]["load_bearing_obligations"] == OBLIGATIONS, "opening obligations")
    require(opening["proof_distance"]["pair_branch_remains_independently_load_bearing"] is True, "opening pair branch")
    require(opening["authority"]["closing_ledger_required"] == "2/9", "opening close ledger")
    require(opening["authority"]["ledger_delta_required"] == "0/9", "opening ledger delta")
    require(opening["authority"]["theorem_promotion_allowed"] is False, "opening promotion")
    require(opening["charter"] == {
        "path": f"{CYCLE_DIR}/CYCLE.md",
        "sha256": PACKAGE_PINS[f"{CYCLE_DIR}/CYCLE.md"][1],
    }, "opening charter pin")
    require(opening["source_pins"] == OPENING_SOURCE_PINS, "opening source pins")

    require(checkpoint["canonical_base_revision"] == CANONICAL, "checkpoint canonical revision")
    require(checkpoint["canonical_base_tree"] == CANONICAL_TREE, "checkpoint canonical tree")
    require(checkpoint["opening_revision"] == OPENING, "checkpoint opening revision")
    require(checkpoint["opening_tree"] == OPENING_TREE, "checkpoint opening tree")
    require(checkpoint["integrated_lane_head"] == INTEGRATED, "checkpoint integrated revision")
    require(checkpoint["integrated_lane_tree"] == INTEGRATED_TREE, "checkpoint integrated tree")
    require(checkpoint["opening_vector"] == OPEN_VECTOR, "checkpoint opening vector")
    require(checkpoint["checkpoint_vector"] == OPEN_VECTOR, "checkpoint vector")
    lane_verdicts = checkpoint["lane_verdicts"]
    require([item["track"] for item in lane_verdicts] == [
        "d3-mixed-carrier-topology",
        "d3-mixed-carrier-falsifier",
        "d3-mixed-carrier-naturality",
    ], "checkpoint lanes")
    require([item["handoff"] for item in lane_verdicts] == ["NULL"] * 3, "checkpoint handoffs")
    require([item["isolated_commit"] for item in lane_verdicts] == [
        EXPECTED_OBJECTS["isolated_topology"]["commit"],
        EXPECTED_OBJECTS["isolated_falsifier"]["commit"],
        EXPECTED_OBJECTS["isolated_naturality"]["commit"],
    ], "checkpoint isolated commits")
    require([item["isolated_tree"] for item in lane_verdicts] == [
        EXPECTED_OBJECTS["isolated_topology"]["tree"],
        EXPECTED_OBJECTS["isolated_falsifier"]["tree"],
        EXPECTED_OBJECTS["isolated_naturality"]["tree"],
    ], "checkpoint isolated trees")
    require(all(item["revision_reachable"] is False for item in lane_verdicts), "checkpoint reachability")
    require(lane_verdicts[1]["universal_negative_found"] is False, "checkpoint universal negative")
    combined = checkpoint["combined_program_status"]
    require(combined["positive_finite_program_found"] is False, "checkpoint positive program")
    require(combined["universal_negative_found"] is False, "checkpoint universal negative")
    require(len(checkpoint["midpoint_conditions"]) == 5, "checkpoint condition count")
    require(all(item["met"] is False for item in checkpoint["midpoint_conditions"]), "checkpoint conditions")
    require(checkpoint["minimum_acceptable_decrease_met"] is False, "checkpoint decrease")
    require(checkpoint["evidence_file_count"] == 6, "checkpoint evidence count")
    decision = checkpoint["checkpoint_decision"]
    require(decision["stop_discovery"] is True, "checkpoint stop")
    require(decision["freeze_claim_dependency_graph"] is True, "checkpoint freeze")
    require(decision["allow_referee_directed_revision"] is False, "checkpoint revision")
    require(decision["construction_started"] is False, "checkpoint construction")
    require(decision["required_close"] == "NULL__STALLED__STOP__SUCCESSOR_NONE", "checkpoint required close")

    require(candidate["canonical_base_revision"] == CANONICAL, "candidate canonical revision")
    require(candidate["canonical_base_tree"] == CANONICAL_TREE, "candidate canonical tree")
    require(candidate["opening_revision"] == OPENING, "candidate opening revision")
    require(candidate["opening_tree"] == OPENING_TREE, "candidate opening tree")
    require(candidate["integrated_evidence_revision"] == INTEGRATED, "candidate integrated revision")
    require(candidate["integrated_evidence_tree"] == INTEGRATED_TREE, "candidate integrated tree")
    require(candidate["checkpoint_revision"] == CHECKPOINT, "candidate checkpoint revision")
    require(candidate["checkpoint_tree"] == CHECKPOINT_TREE, "candidate checkpoint tree")
    require(candidate["opening_ledger"] == "2/9", "candidate opening ledger")
    require(candidate["closing_ledger"] == "2/9", "candidate closing ledger")
    require(candidate["ledger_delta"] == "0/9", "candidate ledger delta")
    require(candidate["theorem_promotion"] == "NONE", "candidate theorem promotion")
    require(candidate["opening_vector"] == OPEN_VECTOR, "candidate opening vector")
    require(candidate["checkpoint_vector"] == OPEN_VECTOR, "candidate checkpoint vector")
    require(candidate["closing_vector"] == CLOSE_VECTOR, "candidate closing vector")
    require(candidate["proof_distance_delta"] == 0, "candidate proof distance")
    require(candidate["trajectory_classification"] == "STALLED", "candidate trajectory")
    require(candidate["overall_handoff"] == "NULL", "candidate handoff")
    require(candidate["strategy_action"] == "STOP", "candidate action")
    require(candidate["selected_successor"] == "NONE", "candidate successor")
    require(candidate["construction_started"] is False, "candidate construction")
    discovery = candidate["discovery_handoffs"]
    require([item["track"] for item in discovery] == [
        "d3-mixed-carrier-topology",
        "d3-mixed-carrier-falsifier",
        "d3-mixed-carrier-naturality",
    ], "candidate discovery lanes")
    require([item["handoff"] for item in discovery] == ["NULL"] * 3, "candidate discovery handoffs")
    programs = candidate["program_status"]
    require(programs["A"]["status"] == "NULL", "candidate A status")
    require(programs["B"]["status"] == "NULL", "candidate B status")
    require(programs["C"]["status"] == "NULL", "candidate C status")
    require(all(programs[key]["complete_finite_program"] is False for key in "ABC"), "candidate complete program overclaim")
    require(programs["B"]["theorem_proved_or_refuted"] is False, "candidate B theorem")
    require(programs["C"]["theorem_proved_or_refuted"] is False, "candidate C theorem")
    require(programs["C"]["triple_escape_proved"] is False, "candidate C escape")
    require(programs["actual_proved_and_replayed_B_plus_C_required_for_D3"] is True, "candidate B+C gate")
    require(candidate["midpoint"]["decision"] == "STOP_DISCOVERY_FREEZE_AND_SEND_TO_REFEREE", "candidate midpoint")
    require(candidate["midpoint"]["referee_directed_revision_allowed"] is False, "candidate revision")
    deltas = candidate["obligation_delta"]
    require([item["id"] for item in deltas] == OBLIGATIONS, "candidate obligation IDs")
    require(all(item["delta"] == "UNCHANGED" for item in deltas), "candidate obligation delta")
    require(all(item["opening"] == item["closing"] for item in deltas), "candidate obligation endpoints")
    face = candidate["joined_face_accounting"]
    require(face["shape_orbits_modulo_active_block_permutation"] == 10, "candidate shape count")
    require(face["formal_labeled_placements_in_one_three_block_family"] == 34, "candidate placement count")
    require(face["taxonomy_coverage"] == "3/10", "candidate taxonomy")
    require(face["end_to_end_denominator"] is False, "candidate denominator")
    triple = candidate["triple_source_accounting"]
    require((triple["total_source_orbits"], triple["settled_source_orbits"]) == (79102449, 77940147), "candidate triple totals")
    require(triple["residual_source_orbits_opening"] == 1162302, "candidate opening residual")
    require(triple["residual_source_orbits_closing"] == 1162302, "candidate closing residual")
    require(triple["residual_delta"] == 0, "candidate residual delta")
    require(triple["source_order_semantic_sha256"] == SOURCE_SEMANTIC_SHA256, "candidate source semantic pin")
    require(triple["is_component_denominator"] is False, "candidate component denominator")
    pair = candidate["pair_accounting"]
    require(pair["global_residual"] == "UNKNOWN", "candidate pair residual")
    require(pair["global_coverage"] == "UNKNOWN", "candidate pair coverage")
    require(pair["certified_global_adjacencies"] == 0, "candidate pair adjacency")
    require(pair["rational_middle_exactness"] == "OPEN", "candidate pair exactness")
    canary = candidate["exact_canary"]
    require((canary["rank_d1"], canary["rank_d2"], canary["rank_C2"]) == (3, 6, 7), "candidate canary ranks")
    require(canary["primitive_relation"] == [-1, 1, 1, 1, 1, 1, 1], "candidate canary relation")
    require(canary["retired_scope"] == "SINGLETON_ONLY_FIXED_BLOCK_ROOT_CARRIERS", "candidate canary scope")
    require(canary["universal_target_A_negative"] is False, "candidate canary universal claim")
    require(canary["D3_counterexample"] is False, "candidate D3 counterexample")
    endpoints = candidate["conditional_endpoints_preserved"]
    require(endpoints["C_exit_predicate"] == "EVERY_VERTEX_OF_A_COMPLETE_COMPONENT_FAITHFUL_GRAPH_REACHES_CERTIFIED_TRUE_PARENT_INFINITY_EQUIVALENTLY_EVERY_SINK_SCC_CONTAINS_IT", "candidate C predicate")
    require(endpoints["C_accepting_input_exists"] is False, "candidate C input gap")
    require(endpoints["actual_compared_pair_complex_exists"] is False, "candidate pair input gap")
    require(candidate["evidence_pins"] == EVIDENCE_PINS, "candidate evidence pins")
    require(candidate["referee_gate"]["producer_acceptance_import_allowed"] is False, "candidate producer import")
    reset = candidate["automatic_reset"]
    require((reset["same_blocker_streak_closing"], reset["zero_ledger_streak_closing"]) == (6, 9), "candidate closing streaks")
    require(reset["action"] == "STOP", "candidate reset action")
    require(candidate["next_strategy"]["eligible_successor_count"] == 0, "candidate successors")
    require(candidate["next_strategy"]["selected_successor"] == "NONE", "candidate selected successor")
    require(candidate["next_strategy"]["construction_authorized"] is False, "candidate next construction")

    require(topology["handoff"] == "NULL" and topology["assessment"] == "DECISIVE_NULL", "topology handoff")
    require(topology["program_status_vector"]["A"]["theorem_proved"] is False, "topology A theorem")
    require(topology["program_status_vector"]["B"]["theorem_proved"] is False, "topology B theorem")
    require(topology["face_type_accounting"]["shape_count"] == 10, "topology shape count")
    require(topology["face_type_accounting"]["source_taxonomy_coverage"] == "3/10", "topology taxonomy")
    require(topology["face_type_accounting"]["source_taxonomy_is_end_to_end_denominator"] is False, "topology denominator")
    require(topology["reachability"]["exact_universal_negative_proved"] is False, "topology universal negative")

    require(falsifier["handoff"] == "NULL", "falsifier handoff")
    require(falsifier["abc_program_status"] == {"A": "A_NULL", "B": "B_NULL", "C": "C_NULL"}, "falsifier statuses")
    require(falsifier["universal_negative_found"] is False, "falsifier universal negative")
    denominator = falsifier["abc_findings"]["B"]["exact_denominator"]
    require((denominator["shape_orbits"], denominator["labeled_placements"]) == (10, 34), "falsifier shape count")
    require(denominator["scope"] == "FORMAL_FACE_COUNT_WITHIN_ONE_LABELED_THREE_BLOCK_FAMILY_NOT_A_SOURCE_CELL_OR_END_TO_END_DENOMINATOR", "falsifier denominator scope")
    require(falsifier["triple_source_accounting"]["semantic_scope"] == "SOURCE_ORDER_AND_ACCOUNTING_ONLY_NOT_COMPONENT_ID_OR_COMPONENT_COUNT", "falsifier source-orbit scope")
    require(falsifier["row2599_canary"]["exact_scope"] == "NO_GO_FOR_SINGLETON_ONLY_FIXED_BLOCK_ROOT_CARRIERS", "falsifier canary scope")
    require("TARGET_A_IMPOSSIBLE" in falsifier["row2599_canary"]["does_not_prove"], "falsifier A caveat")

    require(naturality["handoff"] == "NULL" and naturality["assessment"] == "DECISIVE_NULL", "naturality handoff")
    require(all(naturality["program_status"][key]["status"] == "DECISIVE_NULL" for key in "ABC"), "naturality statuses")
    require(naturality["program_status"]["C"]["first_missing_edge"] == "C-COMP-01", "naturality C first edge")
    c_exit_rows = [row for row in naturality["seam_matrix"] if row["id"] == "C-EXIT-04"]
    require(len(c_exit_rows) == 1 and c_exit_rows[0]["status"] == "PROVED_CONDITIONAL", "naturality conditional exit")
    require("No accepting component-complete input graph exists" in c_exit_rows[0]["gap"], "naturality C input gap")
    require(naturality["revision_reachability"]["target_C_escape_package"] is False, "naturality C reachability")

    shapes, placements = reconstruct_shapes()
    require((shapes, placements) == (10, 34), "independent shape reconstruction")
    require((face["shape_orbits_modulo_active_block_permutation"], face["formal_labeled_placements_in_one_three_block_family"]) == (shapes, placements), "reported shape reconstruction")

    texts = state["texts"]
    require("`NULL` / `DECISIVE_NULL`" in texts["topology_memo"], "topology memo verdict")
    require("not an end-to-end denominator" in texts["topology_memo"], "topology memo denominator")
    require("ten shape orbits and 34 formal labeled placements" in texts["falsifier_memo"], "falsifier memo shape scope")
    require("a component count, or a continuation edge" in texts["falsifier_memo"], "falsifier memo component scope")
    require("PROVED_CONDITIONAL" in texts["naturality_memo"], "naturality memo conditional exit")
    require("accepting input graph does not exist" in texts["naturality_memo"], "naturality memo input gap")
    require("at least twenty-four hostile mutations" in texts["charter"], "charter referee ceiling")
    require("producer acceptance reuse" in texts["work_orders"], "work order fail-closed scope")

    report = texts["report"]
    require(PROTOCOL_PASS_CLAIM in report, "frozen report lost protocol PASS claim")
    require(REPAIR_BLOCK in report, "bounded convergence-label repair changed")
    missing = [phrase for phrase in REQUIRED_REPORT_PHRASES if phrase not in report]
    require(not missing, f"frozen report still misses protocol phrases: {missing}")
    require(
        all(report.count(phrase) == 1 for phrase in REQUIRED_REPORT_PHRASES),
        "mandatory convergence labels must occur exactly once",
    )


def set_path(root: Any, path: tuple[Any, ...], value: Any) -> None:
    target = root
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def change_doc(alias: str, path: tuple[Any, ...], value: Any) -> Callable[[dict[str, Any]], None]:
    return lambda state: set_path(state["docs"][alias], path, copy.deepcopy(value))


def change_object(alias: str, path: tuple[Any, ...], value: Any) -> Callable[[dict[str, Any]], None]:
    return lambda state: set_path(state["objects"][alias], path, copy.deepcopy(value))


def pop_doc(alias: str, path: tuple[Any, ...], index: int) -> Callable[[dict[str, Any]], None]:
    def mutate(state: dict[str, Any]) -> None:
        target: Any = state["docs"][alias]
        for key in path:
            target = target[key]
        target.pop(index)
    return mutate


def replace_text(alias: str, old: str, new: str) -> Callable[[dict[str, Any]], None]:
    def mutate(state: dict[str, Any]) -> None:
        state["texts"][alias] = state["texts"][alias].replace(old, new, 1)
    return mutate


def append_raw(path: str) -> Callable[[dict[str, Any]], None]:
    return lambda state: state["raw"].__setitem__(path, state["raw"][path] + b"X")


HOSTILE_MUTATIONS: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
    ("candidate Git tree", change_object("candidate", ("tree",), "0" * 40)),
    ("candidate Git parent", change_object("candidate", ("parents",), [OPENING])),
    ("checkpoint Git tree", change_object("checkpoint", ("tree",), "0" * 40)),
    ("integrated Git tree", change_object("integrated_evidence", ("tree",), "0" * 40)),
    ("opening Git tree", change_object("opening", ("tree",), "0" * 40)),
    ("canonical Git tree", change_object("canonical", ("tree",), "0" * 40)),
    ("isolated topology tree", change_object("isolated_topology", ("tree",), "0" * 40)),
    ("isolated falsifier tree", change_object("isolated_falsifier", ("tree",), "0" * 40)),
    ("isolated naturality tree", change_object("isolated_naturality", ("tree",), "0" * 40)),
    ("V8 status promotion", change_doc("v8", ("status",), "PROVED")),
    ("V8 ledger promotion", change_doc("v8", ("theorem", "score"), "3/9")),
    ("V8 successor", change_doc("v8", ("theorem_reset_close", "selected_successor"), "D3_CARRIER")),
    ("V8 canary universal negative", change_doc("v8", ("theorem_reset_close", "row2599_chart0_canary", "genuine_mixed_block_carrier_nonexistence_proved"), True)),
    ("opening base commit", change_doc("opening", ("canonical_base", "commit"), "0" * 40)),
    ("opening base tree", change_doc("opening", ("canonical_base", "tree"), "0" * 40)),
    ("opening ledger", change_doc("opening", ("canonical_opening", "ledger"), "3/9")),
    ("opening construction ready", change_doc("opening", ("strategy_evaluation", "construction_ready"), True)),
    ("opening labeled placements", change_doc("opening", ("selected_target", "target_b", "all_labeled_instances_required"), False)),
    ("opening canary globalization", change_doc("opening", ("opening_facts", "flow_triangle_canary", "scope"), "GLOBAL")),
    ("opening triple residual", change_doc("opening", ("opening_facts", "triple_only_accounting", "residual"), 0)),
    ("opening blocker streak", change_doc("opening", ("proof_distance", "opening_vector", 6), 4)),
    ("opening zero-ledger streak", change_doc("opening", ("proof_distance", "opening_vector", 7), 7)),
    ("opening removes pair branch", change_doc("opening", ("proof_distance", "pair_branch_remains_independently_load_bearing"), False)),
    ("opening charter digest", change_doc("opening", ("charter", "sha256"), "0" * 64)),
    ("checkpoint canonical revision", change_doc("checkpoint", ("canonical_base_revision",), "0" * 40)),
    ("checkpoint opening revision", change_doc("checkpoint", ("opening_revision",), "0" * 40)),
    ("checkpoint integrated revision", change_doc("checkpoint", ("integrated_lane_head",), "0" * 40)),
    ("checkpoint opening vector", change_doc("checkpoint", ("opening_vector", 6), 4)),
    ("checkpoint zero streak", change_doc("checkpoint", ("checkpoint_vector", 7), 9)),
    ("topology discovery positive", change_doc("checkpoint", ("lane_verdicts", 0, "handoff"), "POSITIVE")),
    ("falsifier discovery negative", change_doc("checkpoint", ("lane_verdicts", 1, "handoff"), "NEGATIVE")),
    ("naturality discovery timeout", change_doc("checkpoint", ("lane_verdicts", 2, "handoff"), "TIMEOUT")),
    ("checkpoint positive program", change_doc("checkpoint", ("combined_program_status", "positive_finite_program_found"), True)),
    ("checkpoint universal negative", change_doc("checkpoint", ("combined_program_status", "universal_negative_found"), True)),
    ("checkpoint condition met", change_doc("checkpoint", ("midpoint_conditions", 0, "met"), True)),
    ("checkpoint decrease", change_doc("checkpoint", ("minimum_acceptable_decrease_met",), True)),
    ("checkpoint continues discovery", change_doc("checkpoint", ("checkpoint_decision", "stop_discovery"), False)),
    ("checkpoint permits revision", change_doc("checkpoint", ("checkpoint_decision", "allow_referee_directed_revision"), True)),
    ("checkpoint starts construction", change_doc("checkpoint", ("checkpoint_decision", "construction_started"), True)),
    ("candidate canonical revision", change_doc("candidate", ("canonical_base_revision",), "0" * 40)),
    ("candidate checkpoint tree", change_doc("candidate", ("checkpoint_tree",), "0" * 40)),
    ("candidate opening ledger", change_doc("candidate", ("opening_ledger",), "3/9")),
    ("candidate closing ledger", change_doc("candidate", ("closing_ledger",), "3/9")),
    ("candidate ledger delta", change_doc("candidate", ("ledger_delta",), "1/9")),
    ("candidate theorem promotion", change_doc("candidate", ("theorem_promotion",), "D3")),
    ("candidate opening vector", change_doc("candidate", ("opening_vector", 6), 4)),
    ("candidate checkpoint vector", change_doc("candidate", ("checkpoint_vector", 7), 7)),
    ("candidate blocker close", change_doc("candidate", ("closing_vector", 6), 5)),
    ("candidate zero-ledger close", change_doc("candidate", ("closing_vector", 7), 8)),
    ("candidate proof decrease", change_doc("candidate", ("proof_distance_delta",), 1)),
    ("candidate trajectory", change_doc("candidate", ("trajectory_classification",), "CONTINUE")),
    ("candidate handoff", change_doc("candidate", ("overall_handoff",), "POSITIVE")),
    ("candidate action", change_doc("candidate", ("strategy_action",), "CONTINUE")),
    ("candidate successor", change_doc("candidate", ("selected_successor",), "D3_CARRIER")),
    ("candidate construction", change_doc("candidate", ("construction_started",), True)),
    ("candidate topology handoff", change_doc("candidate", ("discovery_handoffs", 0, "handoff"), "POSITIVE")),
    ("candidate falsifier handoff", change_doc("candidate", ("discovery_handoffs", 1, "handoff"), "NEGATIVE")),
    ("candidate naturality handoff", change_doc("candidate", ("discovery_handoffs", 2, "handoff"), "TIMEOUT")),
    ("candidate A status", change_doc("candidate", ("program_status", "A", "status"), "POSITIVE")),
    ("candidate A finite program", change_doc("candidate", ("program_status", "A", "complete_finite_program"), True)),
    ("candidate B finite program", change_doc("candidate", ("program_status", "B", "complete_finite_program"), True)),
    ("candidate C finite program", change_doc("candidate", ("program_status", "C", "complete_finite_program"), True)),
    ("candidate B theorem", change_doc("candidate", ("program_status", "B", "theorem_proved_or_refuted"), True)),
    ("candidate C theorem", change_doc("candidate", ("program_status", "C", "triple_escape_proved"), True)),
    ("candidate drops B+C gate", change_doc("candidate", ("program_status", "actual_proved_and_replayed_B_plus_C_required_for_D3"), False)),
    ("candidate permits revision", change_doc("candidate", ("midpoint", "referee_directed_revision_allowed"), True)),
    ("candidate removes obligation", pop_doc("candidate", ("obligation_delta",), 0)),
    ("candidate closes obligation", change_doc("candidate", ("obligation_delta", 0, "delta"), "CLOSED")),
    ("candidate shape count", change_doc("candidate", ("joined_face_accounting", "shape_orbits_modulo_active_block_permutation"), 9)),
    ("candidate placement count", change_doc("candidate", ("joined_face_accounting", "formal_labeled_placements_in_one_three_block_family"), 33)),
    ("candidate taxonomy", change_doc("candidate", ("joined_face_accounting", "taxonomy_coverage"), "4/10")),
    ("candidate denominator", change_doc("candidate", ("joined_face_accounting", "end_to_end_denominator"), True)),
    ("candidate triple residual", change_doc("candidate", ("triple_source_accounting", "residual_source_orbits_closing"), 0)),
    ("candidate component denominator", change_doc("candidate", ("triple_source_accounting", "is_component_denominator"), True)),
    ("candidate pair residual", change_doc("candidate", ("pair_accounting", "global_residual"), 0)),
    ("candidate canary globalization", change_doc("candidate", ("exact_canary", "retired_scope"), "UNIVERSAL_A_NO_GO")),
    ("candidate C input claimed", change_doc("candidate", ("conditional_endpoints_preserved", "C_accepting_input_exists"), True)),
    ("candidate evidence digest", change_doc("candidate", ("evidence_pins", "ops/team/d3-mixed-carrier-topology/RESULT.json"), "0" * 64)),
    ("falsifier universal negative", change_doc("falsifier", ("universal_negative_found",), True)),
    ("naturality C positive", change_doc("naturality", ("program_status", "C", "status"), "POSITIVE")),
    ("topology positive", change_doc("topology", ("handoff",), "POSITIVE")),
    ("opening source digest", change_doc("opening", ("source_pins", 0, "sha256"), "0" * 64)),
    ("V8 source digest", change_doc("v8", ("source_pins", "ai/omreal/data/CANONICAL_RESEARCH_STATE_V7.json"), "0" * 64)),
    ("remove protocol pass claim", replace_text("report", PROTOCOL_PASS_CLAIM, "| research-cycle protocol | `FAIL` |")),
    ("duplicate convergence label", replace_text("report", "# D3 mixed-carrier theorem-feasibility cycle report", "# D3 mixed-carrier theorem-feasibility cycle report\n\n## Mandatory solution-convergence verdict")),
    ("move candidate byte", append_raw(f"{CYCLE_DIR}/CLOSING_CANDIDATE.json")),
    ("move producer byte", append_raw("ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md")),
]


def run_hostile_mutations(state: dict[str, Any]) -> int:
    rejected = 0
    accepted: list[str] = []
    for name, mutate in HOSTILE_MUTATIONS:
        hostile = copy.deepcopy(state)
        mutate(hostile)
        try:
            validate_contract(hostile)
        except (AuditError, KeyError, IndexError, TypeError):
            rejected += 1
        else:
            accepted.append(name)
    require(not accepted, f"hostile mutations accepted: {accepted}")
    require(rejected == len(HOSTILE_MUTATIONS), "hostile mutation accounting")
    return rejected


def verify_repository_and_sources() -> None:
    require(git_text(["branch", "--show-current"]) == BRANCH, "wrong referee branch")
    head = git_text(["rev-parse", "HEAD"])
    require(head == FROZEN or object_fact(head)["parents"] == [FROZEN], "mutable or multi-commit referee head")
    if head != FROZEN:
        changed = set(git_text(["diff-tree", "--no-commit-id", "--name-only", "-r", head]).splitlines())
        require(changed == {
            f"{REFEREE_DIR}/REVIEW.md",
            f"{REFEREE_DIR}/RESULT.json",
            f"{REFEREE_DIR}/verify_referee.py",
        }, "referee commit changed unauthorized files")
    status_lines = git_text(["status", "--porcelain=v1"]).splitlines()
    require(all(REFEREE_DIR in line for line in status_lines), "non-referee working-tree change")

    for role, expected in EXPECTED_OBJECTS.items():
        require(object_fact(expected["commit"]) == expected, f"{role} object mismatch")

    report_path = f"{CYCLE_DIR}/CYCLE_REPORT.md"
    repair_names = set(
        git_text(["diff", "--name-only", f"{PREFLIGHT}..{FROZEN}"]).splitlines()
    )
    require(repair_names == {report_path}, "v2 repair changed more than CYCLE_REPORT.md")
    require(
        git_text(["diff", "--numstat", f"{PREFLIGHT}..{FROZEN}"]) ==
        f"18\t0\t{report_path}",
        "v2 repair is not the exact 18-line insertion",
    )
    preflight_report = git_bytes(PREFLIGHT, report_path).decode("utf-8")
    repaired_report = git_bytes(FROZEN, report_path).decode("utf-8")
    insertion_anchor = "## Proof-distance and obligation delta"
    require(preflight_report.count(insertion_anchor) == 1, "preflight report anchor")
    expected_repair = preflight_report.replace(
        insertion_anchor, REPAIR_BLOCK + insertion_anchor, 1
    )
    require(repaired_report == expected_repair, "v2 report repair is not mechanical")

    track_files = {
        "isolated_topology": [
            "ops/team/d3-mixed-carrier-topology/RESULT.json",
            "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md",
        ],
        "isolated_falsifier": [
            "ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md",
            "ops/team/d3-mixed-carrier-falsifier/RESULT.json",
        ],
        "isolated_naturality": [
            "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md",
            "ops/team/d3-mixed-carrier-naturality/RESULT.json",
        ],
    }
    for role, files in track_files.items():
        commit = EXPECTED_OBJECTS[role]["commit"]
        ancestry = run_git(["merge-base", "--is-ancestor", commit, FROZEN], check=False)
        require(ancestry.returncode == 1, f"{role} unexpectedly reachable from candidate")
        changed = set(git_text(["diff-tree", "--no-commit-id", "--name-only", "-r", commit]).splitlines())
        require(changed == set(files), f"{role} changed unexpected paths")
        for path in files:
            require(git_bytes(commit, path) == git_bytes(FROZEN, path), f"{role} evidence differs after integration: {path}")

    integrated_diffs = {
        "integrated_topology": track_files["isolated_topology"],
        "integrated_falsifier": track_files["isolated_falsifier"],
        "integrated_evidence": track_files["isolated_naturality"],
    }
    for role, files in integrated_diffs.items():
        changed = set(git_text(["diff-tree", "--no-commit-id", "--name-only", "-r", EXPECTED_OBJECTS[role]["commit"]]).splitlines())
        require(changed == set(files), f"{role} integration changed unexpected paths")

    for path, expected_sha in V8_SOURCE_PINS.items():
        require(sha256(git_bytes(FROZEN, path)) == expected_sha, f"V8 source moved: {path}")
    for pin in OPENING_SOURCE_PINS:
        payload = git_bytes(FROZEN, pin["path"])
        require(len(payload) == pin["bytes"], f"opening source byte count: {pin['path']}")
        require(sha256(payload) == pin["sha256"], f"opening source digest: {pin['path']}")
    for path, expected_sha in EVIDENCE_PINS.items():
        require(sha256(git_bytes(FROZEN, path)) == expected_sha, f"evidence moved: {path}")


def verify_protocol_acceptance() -> str:
    command = [sys.executable, "-B", str(ROOT / "ops/research-team/verify_cycle_protocol.py")]
    process = subprocess.run(
        command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output = (process.stdout + process.stderr).strip()
    require(process.returncode == 0, "protocol replay did not pass on corrected candidate")
    require(
        output == "PASS research-cycle strategy/convergence/storage/publication protocol: 19 cycles, 78 authorized work orders",
        "protocol replay summary changed",
    )
    return output.splitlines()[-1]


def verify_referee_outputs(hostile_count: int) -> None:
    directory = ROOT / REFEREE_DIR
    require({path.name for path in directory.iterdir()} == {
        "REVIEW.md", "RESULT.json", "verify_referee.py"
    }, "referee surface must contain exactly three files")
    result = json.loads((directory / "RESULT.json").read_text(encoding="utf-8"))
    review = (directory / "REVIEW.md").read_text(encoding="utf-8")
    require(result["review_verdict"] == "ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED", "result verdict")
    require(result["referee_handoff"] == "NULL", "result referee handoff")
    require(result["cycle_handoff"] == "NULL", "result cycle handoff")
    require(result["frozen_candidate"] == {"revision": FROZEN, "tree": FROZEN_TREE}, "result frozen candidate")
    require(result["protocol_replay"]["status"] == "PASS", "result protocol status")
    require(result["protocol_replay"]["missing_required_phrases"] == [], "result protocol phrases")
    require(result["hostile_mutations"]["rejected"] == hostile_count, "result hostile count")
    require(result["hostile_mutations"]["accepted"] == 0, "result hostile acceptance")
    require("ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED" in review, "review verdict")
    require("referee handoff: `NULL`" in review, "review referee handoff")
    require("cycle handoff: `NULL`" in review, "review cycle handoff")
    require(PROTOCOL_PASS_CLAIM in review, "review protocol pass claim")
    require("v1 preflight rejection" in review, "review preflight disclosure")


def main() -> None:
    verify_repository_and_sources()
    state = load_state()
    validate_contract(state)
    shape_count = reconstruct_shapes()
    exit_cases = exit_predicate_equivalence_cases()
    protocol_summary = verify_protocol_acceptance()
    hostile_count = run_hostile_mutations(state)
    verify_referee_outputs(hostile_count)
    print("PASS independent frozen-object and source/evidence pin reconstruction")
    print(f"PASS shape reconstruction {shape_count[0]} orbits / {shape_count[1]} labeled placements")
    print(f"PASS conditional C sink-SCC equivalence on {exit_cases} finite fixtures; accepting input remains absent")
    print(f"PASS hostile mutations rejected {hostile_count}/{hostile_count}")
    print(f"PASS corrected protocol replay: {protocol_summary}")
    print("VERDICT ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED handoff=NULL cycle=NULL")


if __name__ == "__main__":
    main()
