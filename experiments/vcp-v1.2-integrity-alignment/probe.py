#!/usr/bin/env python3
"""Pinned-source observation probe, not a normative or production verifier.

Separate implementation prepared on 2026-10-24. The earlier reported probe at
1b88644 was unavailable and is not reproduced by identity here. No network I/O.
"""

import argparse
import ast
import hashlib
import importlib.metadata
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Tuple

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

VCP_REV = "b23acb266f88df81d960d36d58fb64ceaa0dd5ed"
VAP_REV = "277b37930be858c0832708a8696d6f213b1fe7bb"
RTA_REV = "3d359dce3be479632d41e4dee74c7f102766e202"
SPEC_PATH = "spec/v1.2/VCP-Specification-v1_2_en.md"
VAP_PATH = "spec/v1.2/VAP_Framework_Specification.md"
QUICK_PATH = "examples/python/quickstart.py"
RTA_PATH = "tools/verifier/vcp_verifier.py"
EXPECTED = {
    SPEC_PATH: "ce94399bde111c8b805d3804fad2e6d61cab2f1839533d5009e94e812d15a942",
    VAP_PATH: "dbe2439d6d138929b48697cd0545a5c8324059ab032732b9a9122f993fde9f48",
    QUICK_PATH: "7f8351344667c349bd7d1c7897f388459f2548e58525e0c63d8b731b57279881",
    RTA_PATH: "6d9fb91f268c0af1cf898a0e1a608852825d46952d13a544411634e91518c959",
}


def sha(data):
    return hashlib.sha256(data).digest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True
    ).stdout


def read_source(repo, rev, path, sources):
    data = git(repo, "show", f"{rev}:{path}")
    digest = sha(data).hex()
    if path in EXPECTED:
        require(digest == EXPECTED[path], f"Unexpected pinned source bytes: {path}")
    sources.append({"revision": rev, "path": path, "sha256": digest})
    return data.decode("utf-8")


def functions(texts, names, namespace):
    """Only reviewed pure function definitions from hash-checked source files.

    No module main block, imports, decorators, I/O or quickstart networking is
    executed. Hash checks above precede this function; AST selection alone is
    not intended as a sandbox for arbitrary supplied Python.
    """
    found = []
    for text in texts:
        for node in ast.parse(text).body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                require(not node.decorator_list, "Unexpected decorator")
                found.append(node)
    require(sorted(n.name for n in found) == sorted(names), "Missing/duplicate source function")
    exec(compile(ast.Module(body=found, type_ignores=[]), "pinned-reviewed-functions", "exec"), namespace)


def mth(entries):
    """Recursive tree construction specified by RFC 6962 and RFC 9162."""
    if not entries:
        return sha(b"")
    if len(entries) == 1:
        return sha(b"\x00" + entries[0])
    k = 1 << ((len(entries) - 1).bit_length() - 1)
    return sha(b"\x01" + mth(entries[:k]) + mth(entries[k:]))


def rfc_path(entries, index):
    if len(entries) == 1:
        return []
    k = 1 << ((len(entries) - 1).bit_length() - 1)
    if index < k:
        return rfc_path(entries[:k], index) + [mth(entries[k:])]
    return rfc_path(entries[k:], index - k) + [mth(entries[:k])]


def strict(entry, index, size, path, root):
    """Size-dependent inclusion verification, RFC 9162 section 2.1.3.2."""
    if not 0 <= index < size:
        return False
    fn, sn = index, size - 1
    current = sha(b"\x00" + entry)
    for sibling in path:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            current = sha(b"\x01" + sibling + current)
            if not fn & 1:
                while fn and not fn & 1:
                    fn >>= 1
                    sn >>= 1
        else:
            current = sha(b"\x01" + current + sibling)
        fn >>= 1
        sn >>= 1
    return sn == 0 and current == root


def fold(entry, path):
    current = sha(b"\x00" + entry)
    for step in path:
        sibling = bytes.fromhex(step["hash"])
        current = sha(b"\x01" + (sibling + current if step["position"] == "left" else current + sibling))
    return current


def signature_valid(public_key, signature, message):
    try:
        public_key.verify(signature, message)
        return True
    except InvalidSignature:
        return False


def run(args):
    require(importlib.metadata.version("rfc8785") == "0.1.4", "Use pinned rfc8785==0.1.4")
    sources = []
    spec = read_source(args.vcp_spec, VCP_REV, SPEC_PATH, sources)
    quick = read_source(args.vcp_spec, VCP_REV, QUICK_PATH, sources)
    vap = read_source(args.vap_spec, VAP_REV, VAP_PATH, sources)
    rta_bytes = args.rta_verifier.read_bytes()
    require(sha(rta_bytes).hex() == EXPECTED[RTA_PATH], "Unexpected RTA verifier bytes")
    sources.append({"revision": RTA_REV, "path": RTA_PATH, "sha256": sha(rta_bytes).hex()})
    ns = {"hashlib": hashlib, "json": json, "List": List, "Dict": Dict, "Tuple": Tuple, "MerkleTree": SimpleNamespace}
    functions(re.findall(r"```python\n(.*?)```", spec, re.S),
              {"merkle_hash", "build_merkle_tree", "generate_audit_path"}, ns)
    functions([quick], {"verify_merkle_proof"}, ns)
    functions([rta_bytes.decode()], {"sha256_hex", "rfc6962_leaf_hash", "rfc6962_node_hash", "compute_rfc6962_merkle_root", "verify_event_hash"}, ns)

    entries = [sha(f"synthetic-event-{i}".encode()) for i in range(64)]
    selfchecks = 0
    for n in range(1, 65):
        for i in range(n):
            path = rfc_path(entries[:n], i)
            root = mth(entries[:n])
            require(strict(entries[i], i, n, path, root), "RFC positive control failed")
            require(not strict(b"modified-entry", i, n, path, root), "RFC modified entry accepted")
            require(not strict(entries[i], i, n, path + [b"\0" * 32], root), "RFC surplus path accepted")
            if path:
                require(not strict(entries[i], i, n, path[:-1], root), "RFC truncated path accepted")
            selfchecks += 1

    different, failures, quick_pass = [], [], 0
    for n in range(1, 17):
        tree = ns["build_merkle_tree"]([b.hex() for b in entries[:n]])
        if tree.root != mth(entries[:n]):
            different.append(n)
        for i in range(n):
            path = ns["generate_audit_path"](tree, i)
            if fold(entries[i], path) != tree.root:
                failures.append([n, i])
            quick_pass += ns["verify_merkle_proof"](entries[i].hex(), path, tree.root.hex())
    small = ns["build_merkle_tree"]([b.hex() for b in entries[:3]])
    duplicate = ns["build_merkle_tree"]([b.hex() for b in entries[:3] + entries[2:3]])

    tree8 = ns["build_merkle_tree"]([b.hex() for b in entries[:8]])
    # Deliberately public synthetic key. Never use this key for real evidence.
    key = Ed25519PrivateKey.from_private_bytes(sha(b"PUBLIC SYNTHETIC REVIEW KEY"))
    signature = key.sign(tree8.root)
    original = {"MerkleRoot": tree8.root.hex(), "EventCount": 8, "FirstEventID": "e0", "LastEventID": "e7", "PolicyID": "p0"}
    edited = {**original, "EventCount": 6, "LastEventID": "e5", "PolicyID": "p1"}
    require(signature_valid(key.public_key(), signature, tree8.root), "Signature positive control failed")
    require(not signature_valid(key.public_key(), signature, sha(b"changed root")), "Signature negative control failed")
    size6 = []
    for i in range(6):
        path = ns["generate_audit_path"](tree8, i)
        size6.append({"index": i, "size_free_fold": fold(entries[i], path) == tree8.root,
                      "generic_depth": len(path) == math.ceil(math.log2(6)),
                      "strict_size6": strict(entries[i], i, 6, [bytes.fromhex(p["hash"]) for p in path], tree8.root)})

    # Illustrations of explicitly stated preimages, not a normative E definition.
    header, payload = {"EventID": "synthetic-0"}, {"value": "sample"}
    joined = rfc8785.dumps(header) + rfc8785.dumps(payload)
    vcp_leaf = sha(b"\x00" + sha(joined))
    event_body = {"Header": header, "Payload": payload}
    vap_b_leaf = sha(b"\x00" + rfc8785.dumps(event_body))
    prev_hash_example = b"\0" * 32

    rta_header, rta_payload = {"EventID": "sample", "Note": "é"}, {"Price": "1.25"}
    jcs_input = rfc8785.dumps(rta_header) + rfc8785.dumps(rta_payload)
    json_input = (json.dumps(rta_header, sort_keys=True) + json.dumps(rta_payload, sort_keys=True)).encode()
    sample = {"Header": rta_header, "Payload": rta_payload, "Security": {"EventHash": sha(jcs_input).hex()}}
    jcs_accepted, _ = ns["verify_event_hash"](sample)
    sample["Security"]["EventHash"] = sha(json_input).hex()
    dumps_accepted, _ = ns["verify_event_hash"](sample)

    numeric = []
    fixtures = git(args.vcp_spec, "ls-tree", "-r", "--name-only", VCP_REV, "--", "tests/fixtures/v1.2/valid").decode().splitlines()
    fixtures = sorted(p for p in fixtures if p.endswith(".json"))
    require(len(fixtures) == 40, "Unexpected valid-fixture inventory")
    for path in fixtures:
        raw = read_source(args.vcp_spec, VCP_REV, path, sources)
        fixture_header = json.loads(raw)["Header"]
        n = fixture_header["TimestampInt"]
        require(type(n) is int, "TimestampInt is not a JSON integer")
        try:
            rfc8785.dumps(fixture_header)
            native = "accepted"
        except rfc8785.IntegerDomainError:
            native = "IntegerDomainError"
        exact = int(float(n)) == n
        # Diagnostic only: never round a value to make a fixture pass.
        encoded = rfc8785.dumps({**fixture_header, "TimestampInt": float(n)}) if exact else None
        numeric.append({"file": path, "timestamp": n, "exact_binary64": exact,
                        "python_integer_input": native, "exact_double_input_accepted": encoded is not None})

    markers = [*(f"EH-00{i}" for i in range(1, 7)), *(f"PRV-00{i}" for i in range(1, 4)),
               "anchor_sequence", "prev_anchor_record_hash", "VerifyChain", "VSO-VAP-RD-001"]
    return {
        "status": "research_observation_unadopted_not_conformance_verdict",
        "provenance": "Separate reconstruction from pinned public sources; not the unavailable probe at 1b88644.",
        "environment": {"python": sys.version.split()[0], "rfc8785": importlib.metadata.version("rfc8785"),
                        "cryptography": importlib.metadata.version("cryptography")},
        "sources": sources,
        "rfc_controls": {"tree_sizes": [1, 64], "positive_inclusions": selfchecks,
                         "modified_entries_and_surplus_paths_rejected": True, "nonempty_paths_truncated_rejected": True},
        "P1": {"tree_sizes": [1, 16], "different_root_sizes": different},
        "P2": {"proof_count": 136, "own_root_failure_count": len(failures), "failures_size_index": failures},
        "P3": {"proof_count": 136, "quickstart_pass_count": quick_pass},
        "P4": {"three_vs_duplicate_four_same_vcp_root": small.root == duplicate.root,
               "three_vs_duplicate_four_same_rfc_root": mth(entries[:3]) == mth(entries[:3] + entries[2:3])},
        "P5": {"kind": "illustrative_preimage_comparison_not_profile_mapping", "vcp_leaf": vcp_leaf.hex(),
               "vap_b_leaf_assuming_E_is_Header_Payload_object": vap_b_leaf.hex(),
               "same_leaf_under_that_reading": vcp_leaf == vap_b_leaf,
               "vcp_unchained_event_hash": sha(joined).hex(),
               "vap_A_with_32_zero_byte_prev_hash_example": sha(joined + prev_hash_example).hex()},
        "P6": {"scope": "published_root_only_signature_example_and_synthetic_batch", "original_record": original,
               "edited_record": edited, "signature_hex": signature.hex(),
               "root_only_signature_valid_after_metadata_edit": signature_valid(key.public_key(), signature, bytes.fromhex(edited["MerkleRoot"])),
               "claimed_size6": size6},
        "P7": {"target": "reference tool describing itself as VCP v1.1", "jcs_bytes_hex": jcs_input.hex(),
               "json_dumps_bytes_hex": json_input.hex(), "jcs_event_hash_accepted": jcs_accepted,
               "json_dumps_event_hash_accepted": dumps_accepted,
               "three_leaf_root_matches_vcp_odd_duplicate_example": ns["compute_rfc6962_merkle_root"]([b.hex() for b in entries[:3]]) == small.root.hex()},
        "P8": {"fixture_count": len(numeric), "rejected_as_python_integers": sum(r["python_integer_input"] != "accepted" for r in numeric),
               "exact_binary64_count": sum(r["exact_binary64"] for r in numeric),
               "accepted_as_exact_doubles": sum(r["exact_double_input_accepted"] for r in numeric),
               "nearby_lossy_example": {"integer": numeric[0]["timestamp"] + 1, "after_binary64_conversion": int(float(numeric[0]["timestamp"] + 1))},
               "fixtures": numeric},
        "P9": {"status": "historical_regression_unverified_originals_unavailable",
               "public_marker_presence_only": {m: m in vap for m in markers}, "MiFID_II_III_present": "MiFID II/III" in vap,
               "warning": "Absent markers do not establish prior approval, normative adoption, or historical loss."},
        "limits": ["No production implementation, K3 fixture, customer system or external anchor tested.",
                   "No changes to specifications, existing verifier/gates, fixed distribution, DOC-SYNC or K3.",
                   "Internal recomputation is not independent third-party reproduction."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vcp-spec", type=Path, required=True, help="Repository containing the pinned VCP commit")
    parser.add_argument("--vap-spec", type=Path, required=True, help="Repository containing the pinned VAP commit")
    parser.add_argument("--rta-verifier", type=Path, required=True, help="Exact pinned reference verifier source file (hash checked)")
    parser.add_argument("--output", type=Path, help="Write result JSON; otherwise print it")
    parser.add_argument("--check", type=Path, help="Compare all non-environment results with a saved report")
    args = parser.parse_args()
    try:
        result = run(args)
        if args.check:
            expected = json.loads(args.check.read_text())
            require({k: v for k, v in result.items() if k != "environment"} ==
                    {k: v for k, v in expected.items() if k != "environment"}, "Observation output differs from saved report")
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered)
        else:
            print(rendered, end="")
        return 0
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Probe could not complete: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
