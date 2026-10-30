"""Boundary agreement for the experimental demo contract.

The committed fixtures are read-only inputs. Mutations are written to temporary
files and checked through the Python API and the Node CLI. Structural and
relational mutations are re-signed with the published synthetic TEST seeds so
that an unrelated stale signature cannot make a broken boundary check pass.
These tests do not establish VAP conformance or independent verification.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

DEMO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO_DIR))
import verify_python as verifier  # noqa: E402

CONTRACT_ID = "vap-interop-demo/0.2.0"
MAX_INPUT_BYTES = 2 * 1024 * 1024
SUCCESS_CHECKS = [
    "contract-and-shape",
    "pinned-scope",
    "event-signatures",
    "sequence-and-scope",
    "rfc6962-root",
    "role-receipts",
    "attempt-outcome-bijection",
]
FIXTURE_NAMES = (
    "valid-pack.json",
    "valid-six-events.json",
    "invalid-tampered-event.json",
    "invalid-omitted-outcome.json",
    "invalid-split-view.json",
    "invalid-omitted-pair.json",
    "invalid-rebound-scope.json",
    "invalid-untrusted-signer.json",
)
RECORD_ROLES = {
    "producer_manifest": "producer",
    "observer_receipt": "observer",
    "demo_anchor_receipt": "anchor",
}
TEST_KEYS = {
    role: Ed25519PrivateKey.from_private_bytes(bytes([seed]) * 32)
    for role, seed in (("producer", 0x11), ("observer", 0x22), ("anchor", 0x33))
}
NODE_PARSE_PROBE = r"""
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const { strictParse, VerificationError } =
  await import(pathToFileURL(process.argv[2]).href);
try {
  const value = strictParse(fs.readFileSync(process.argv[3], "utf8"));
  process.stdout.write(JSON.stringify({ accepted: true, value }) + "\n");
} catch (error) {
  if (!(error instanceof VerificationError)) {
    process.stderr.write(String(error) + "\n");
    process.exit(2);
  }
  process.stdout.write(JSON.stringify({ accepted: false }) + "\n");
  process.exit(1);
}
"""


def wire(value):
    """Ordinary JSON for a temporary input, with no fixture writes."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def signing_bytes(value):
    """Encode test mutations; intentionally do not enforce contract shapes."""
    return wire(value)


def test_signature(body, role):
    return base64.b64encode(TEST_KEYS[role].sign(signing_bytes(body))).decode("ascii")


def resign_record(pack, field, role):
    record = pack[field]
    record["signature"] = test_signature(
        {key: value for key, value in record.items() if key != "signature"}, role
    )


def reference_root(events):
    """RFC 6962 split used only to repair unrelated integrity after mutations."""
    leaves = [
        hashlib.sha256(b"\x00" + signing_bytes(event)).digest()
        for event in events
    ]

    def mth(nodes):
        if not nodes:
            return hashlib.sha256(b"").digest()
        if len(nodes) == 1:
            return nodes[0]
        split = 1 << ((len(nodes) - 1).bit_length() - 1)
        return hashlib.sha256(b"\x01" + mth(nodes[:split]) + mth(nodes[split:])).digest()

    return mth(leaves).hex()


def bind_records(pack, trust, record_signers=None):
    scope_hash = hashlib.sha256(signing_bytes(pack["scope"])).hexdigest()
    pack["scope_commitment"] = scope_hash
    trust["scope_commitment"] = scope_hash
    root = reference_root(pack["events"])
    pack["merkle"]["root"] = root
    for field, role in RECORD_ROLES.items():
        record = pack[field]
        record["merkle_root"] = root
        record["scope_commitment"] = scope_hash
        record["event_count"] = len(pack["events"])
        resign_record(pack, field, (record_signers or {}).get(field, role))


def resign(pack, trust, event_signers=None, record_signers=None):
    for index, event in enumerate(pack["events"]):
        unsigned = {
            key: value for key, value in event.items()
            if key not in {"payload_hash", "signature"}
        }
        event["payload_hash"] = hashlib.sha256(signing_bytes(unsigned)).hexdigest()
        event["signature"] = test_signature(
            {key: value for key, value in event.items() if key != "signature"},
            (event_signers or {}).get(index, "producer"),
        )
    bind_records(pack, trust, record_signers)


def reverse_objects(value):
    if isinstance(value, dict):
        return {
            key: reverse_objects(item)
            for key, item in reversed(list(value.items()))
        }
    if isinstance(value, list):
        return [reverse_objects(item) for item in value]
    return value


def nonzero_pad_bits(encoded):
    """Preserve decoded bytes but violate canonical base64 unused-bit rules."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    padding = len(encoded) - len(encoded.rstrip("="))
    if padding not in (1, 2):
        raise AssertionError("The fixture must use padded base64")
    position = len(encoded) - padding - 1
    index = alphabet.index(encoded[position])
    if index & 1:
        raise AssertionError("The original encoding must have zero pad bits")
    return encoded[:position] + alphabet[index | 1] + encoded[position + 1:]


class ContractBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        if cls.node is None:
            raise RuntimeError("Node is required; boundary agreement must not be skipped")
        cls.node_script = DEMO_DIR / "verify_node.mjs"
        # Load all eight existing vectors without rewriting any source file.
        cls.fixture_bytes = {
            name: (DEMO_DIR / "test-vectors" / name).read_bytes()
            for name in FIXTURE_NAMES
        }
        cls.pack = json.loads(cls.fixture_bytes["valid-pack.json"])
        cls.six_pack = json.loads(cls.fixture_bytes["valid-six-events.json"])
        cls.trust = json.loads((DEMO_DIR / "test-vectors" / "demo-trust.json").read_bytes())
        cls.six_trust = json.loads(
            (DEMO_DIR / "test-vectors" / "demo-trust-six.json").read_bytes()
        )

    def fresh(self):
        return copy.deepcopy(self.pack), copy.deepcopy(self.trust)

    def assert_cli_result(self, completed, expected):
        expected_exit = 0 if expected == "PASS" else 1
        self.assertEqual(
            completed.returncode, expected_exit,
            f"stdout={completed.stdout[:2000]!r}; stderr={completed.stderr[:2000]!r}",
        )
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"Expected one JSON result, got {completed.stdout[:2000]!r}: {exc}")
        self.assertEqual(
            set(result), {"contract_id", "verdict", "checks", "error"}
        )
        self.assertEqual(result["contract_id"], CONTRACT_ID)
        self.assertEqual(result["verdict"], expected)
        self.assertIsInstance(result["checks"], list)
        if expected == "PASS":
            self.assertEqual(result["checks"], SUCCESS_CHECKS)
            self.assertIsNone(result["error"])
        else:
            self.assertIsInstance(result["error"], str)
            self.assertTrue(result["error"])

    def assert_raw_result(self, pack_bytes, trust_bytes, expected="FAIL"):
        with tempfile.TemporaryDirectory(prefix="vap-demo-boundary-") as temporary:
            directory = Path(temporary)
            pack_path = directory / "pack.json"
            trust_path = directory / "trust.json"
            pack_path.write_bytes(pack_bytes)
            trust_path.write_bytes(trust_bytes)
            if expected == "PASS":
                checks = verifier.verify_pack(
                    verifier.load_json(pack_path), verifier.load_json(trust_path)
                )
                self.assertEqual(checks, SUCCESS_CHECKS)
            else:
                with self.assertRaises(verifier.VerificationError):
                    verifier.verify_pack(
                        verifier.load_json(pack_path), verifier.load_json(trust_path)
                    )
            completed = subprocess.run(
                [
                    self.node, str(self.node_script), str(pack_path),
                    "--trust", str(trust_path), "--json",
                ],
                capture_output=True, text=True, timeout=20, check=False,
            )
            self.assert_cli_result(completed, expected)

    def assert_both(self, pack, trust, expected="FAIL"):
        self.assert_raw_result(wire(pack), wire(trust), expected)

    def assert_parser(self, raw, accepted):
        if accepted:
            parsed = verifier.strict_loads(raw)
        else:
            with self.assertRaises(verifier.VerificationError):
                verifier.strict_loads(raw)
        with tempfile.TemporaryDirectory(prefix="vap-demo-parser-") as temporary:
            raw_path = Path(temporary) / "raw.json"
            probe_path = Path(temporary) / "parser-probe.mjs"
            raw_path.write_bytes(raw.encode("utf-8"))
            probe_path.write_text(NODE_PARSE_PROBE, encoding="utf-8")
            completed = subprocess.run(
                [
                    self.node, str(probe_path),
                    str(self.node_script), str(raw_path),
                ],
                capture_output=True, text=True, timeout=20, check=False,
            )
            self.assertEqual(
                completed.returncode, 0 if accepted else 1,
                f"stdout={completed.stdout[:2000]!r}; stderr={completed.stderr[:2000]!r}",
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["accepted"], accepted)
            if accepted:
                self.assertEqual(result["value"], parsed)

    def test_permitted_whitespace_key_order_and_ascii_escapes(self):
        raw = json.dumps(reverse_objects(self.six_pack), indent=2).encode("ascii")
        raw = raw.replace(
            b'"vap-interop-demo/0.2.0"', b'"\\u0076ap-interop-demo/0.2.0"', 1
        )
        self.assert_raw_result(raw, wire(self.six_trust), "PASS")

    def test_scalar_and_safe_integer_parser_boundaries(self):
        accepted = [
            "0", "9007199254740991", "-9007199254740991",
            '[true,false,null," ~"]', '{"\\u0061":1}',
        ]
        rejected = [
            "9007199254740992", "-9007199254740992",
            "1.0", "1e0", "1E+0", "-0", "-0.0",
            "NaN", "Infinity", "-Infinity", "1e309",
        ]
        for raw in accepted:
            with self.subTest(raw=raw, accepted=True):
                self.assert_parser(raw, True)
        for raw in rejected:
            with self.subTest(raw=raw, accepted=False):
                self.assert_parser(raw, False)

    def test_number_token_rejection_in_otherwise_signed_pack(self):
        original = wire(self.pack)
        needle = b'"sequence_no":1,'
        self.assertIn(needle, original)
        for token in (b"1.0", b"1e0", b"1E+0", b"-0", b"9007199254740992"):
            with self.subTest(token=token):
                raw = original.replace(
                    needle, b'"sequence_no":' + token + b",", 1
                )
                self.assert_raw_result(raw, wire(self.trust))

    def test_duplicate_keys_include_equal_and_escaped_equivalents(self):
        pack = wire(self.pack)
        trust = wire(self.trust)
        contract = wire(CONTRACT_ID)
        cases = {
            "pack-root": (
                b'{"contract_id":' + contract + b"," + pack[1:], trust
            ),
            "pack-escaped-root": (
                b'{"\\u0063ontract_id":' + contract + b"," + pack[1:], trust
            ),
            "pack-nested-scope": (
                pack.replace(
                    b'"scope":{',
                    b'"scope":{"chain_id":' + wire(self.pack["scope"]["chain_id"]) + b",",
                    1,
                ),
                trust,
            ),
            "trust-root": (
                pack, b'{"contract_id":' + contract + b"," + trust[1:]
            ),
            "trust-nested-role": (
                pack,
                trust.replace(
                    b'"producer":{',
                    b'"producer":{"key_id":' + wire(self.trust["roles"]["producer"]["key_id"]) + b",",
                    1,
                ),
            ),
        }
        for name, (pack_raw, trust_raw) in cases.items():
            with self.subTest(name=name):
                self.assert_raw_result(pack_raw, trust_raw)

    def test_unicode_control_bom_and_invalid_utf8_are_rejected(self):
        for raw in (
            '"é"', '"\\u00e9"', '{"é":1}', '{"\\u00e9":1}',
            '"\\u001f"', '"\\u007f"', '"A\\n"', '"A\\r"',
            '{"A\\n":1}', '"\\ud800"', '"\\ud83d\\ude00"',
        ):
            with self.subTest(raw=raw):
                self.assert_parser(raw, False)
        pack, trust = wire(self.pack), wire(self.trust)
        for name, pack_raw, trust_raw in (
            ("pack-bom", b"\xef\xbb\xbf" + pack, trust),
            ("trust-bom", pack, b"\xef\xbb\xbf" + trust),
            ("pack-invalid-utf8", b"\xff" + pack, trust),
            ("trust-invalid-utf8", pack, b"\xff" + trust),
        ):
            with self.subTest(name=name):
                self.assert_raw_result(pack_raw, trust_raw)

    def test_depth_limit_counts_root_as_zero(self):
        self.assert_parser("[" * 16 + "0" + "]" * 16, True)
        self.assert_parser("[" * 17 + "0" + "]" * 17, False)

    def test_input_file_byte_limit(self):
        pack, trust = wire(self.pack), wire(self.trust)
        exact_limit = pack + b" " * (MAX_INPUT_BYTES - len(pack))
        self.assert_raw_result(exact_limit, trust, "PASS")
        self.assert_raw_result(exact_limit + b" ", trust)
        oversized_trust = trust + b" " * (MAX_INPUT_BYTES + 1 - len(trust))
        self.assert_raw_result(pack, oversized_trust)

    def test_identifier_length_bounds(self):
        pack, trust = self.fresh()
        pack["events"][0]["model_id"] = "A" * 1024
        resign(pack, trust)
        self.assert_both(pack, trust, "PASS")
        for identifier in ("", "A" * 1025, "model\n", "model\r"):
            with self.subTest(length=len(identifier), suffix=repr(identifier[-8:])):
                pack, trust = self.fresh()
                pack["events"][0]["model_id"] = identifier
                resign(pack, trust)
                self.assert_both(pack, trust)

    def test_unknown_fields_at_every_object_level(self):
        cases = (
            "pack", "scope", "event", "provenance", "context",
            "merkle", "receipt", "trust", "roles", "role",
        )
        for name in cases:
            with self.subTest(object=name):
                pack, trust = self.fresh()
                attempt = next(
                    event for event in pack["events"]
                    if event["event_type"] == "AI_DECISION_ATTEMPT"
                )
                target = {
                    "pack": pack,
                    "scope": pack["scope"],
                    "event": attempt,
                    "provenance": attempt["provenance"],
                    "context": attempt["provenance"]["context"],
                    "merkle": pack["merkle"],
                    "receipt": pack["producer_manifest"],
                    "trust": trust,
                    "roles": trust["roles"],
                    "role": trust["roles"]["producer"],
                }[name]
                target["unexpected"] = 0
                resign(pack, trust)
                self.assert_both(pack, trust)

    def test_missing_required_fields(self):
        for name in (
            "pack", "scope", "event", "provenance", "context",
            "merkle", "receipt", "trust",
        ):
            with self.subTest(object=name):
                pack, trust = self.fresh()
                attempt = next(
                    event for event in pack["events"]
                    if event["event_type"] == "AI_DECISION_ATTEMPT"
                )
                target, key = {
                    "pack": (pack, "canonicalization"),
                    "scope": (pack["scope"], "policy_id"),
                    "event": (attempt, "model_id"),
                    "provenance": (attempt["provenance"], "action"),
                    "context": (attempt["provenance"]["context"], "jurisdiction"),
                    "merkle": (pack["merkle"], "algorithm"),
                    "receipt": (pack["producer_manifest"], "issued_at"),
                    "trust": (trust, "trust_version"),
                }[name]
                del target[key]
                resign(pack, trust)
                self.assert_both(pack, trust)

    def test_contract_algorithm_and_event_enums(self):
        for name, value in (
            ("contract_id", "vap-interop-demo/0.1.0"),
            ("canonicalization", "RFC8785"),
            ("hash_algorithm", "SHA-512"),
            ("signature_algorithm", "RSA"),
            ("merkle.algorithm", "DUPLICATE-LAST-SHA256"),
            ("event_type", "UNSCOPED_EVENT"),
            ("outcome", "UNKNOWN"),
            ("human_review_required", 0),
            ("record_type", "OBSERVER_RECEIPT"),
        ):
            with self.subTest(field=name):
                pack, trust = self.fresh()
                if name == "merkle.algorithm":
                    pack["merkle"]["algorithm"] = value
                elif name == "event_type":
                    pack["events"][0]["event_type"] = value
                elif name in {"outcome", "human_review_required"}:
                    outcome = next(
                        event for event in pack["events"]
                        if event["event_type"] == "AI_DECISION_OUTCOME"
                    )
                    outcome["provenance"][name] = value
                elif name == "record_type":
                    pack["producer_manifest"]["record_type"] = value
                else:
                    pack[name] = value
                resign(pack, trust)
                self.assert_both(pack, trust)

    def test_boolean_is_not_a_count_or_sequence_number(self):
        pack, trust = self.fresh()
        attempt = next(
            event for event in pack["events"]
            if event["event_type"] == "AI_DECISION_ATTEMPT"
        )
        outcome = next(
            event for event in pack["events"]
            if event["event_type"] == "AI_DECISION_OUTCOME"
            and event["provenance"]["attempt_id"] == attempt["provenance"]["attempt_id"]
        )
        one_pair = copy.deepcopy([attempt, outcome])
        for index, event in enumerate(one_pair, 1):
            event["sequence_no"] = index
        pack["events"] = one_pair
        pack["scope"]["expected_attempt_count"] = 1
        resign(pack, trust)
        self.assert_both(pack, trust, "PASS")
        pack["scope"]["expected_attempt_count"] = True
        resign(pack, trust)
        self.assert_both(pack, trust)

        pack, trust = self.fresh()
        pack["events"][0]["sequence_no"] = True
        resign(pack, trust)
        self.assert_both(pack, trust)

        pack, trust = self.fresh()
        pack["producer_manifest"]["event_count"] = True
        resign_record(pack, "producer_manifest", "producer")
        self.assert_both(pack, trust)

    def test_event_cannot_use_a_valid_observer_role_signature(self):
        pack, trust = self.fresh()
        pack["events"][0]["key_id"] = trust["roles"]["observer"]["key_id"]
        resign(pack, trust, event_signers={0: "observer"})
        self.assert_both(pack, trust)

    def test_receipts_cannot_use_other_valid_role_keys(self):
        wrong_roles = {
            "producer_manifest": "observer",
            "observer_receipt": "anchor",
            "demo_anchor_receipt": "producer",
        }
        for field, wrong_role in wrong_roles.items():
            with self.subTest(field=field):
                pack, trust = self.fresh()
                pack[field]["key_id"] = trust["roles"][wrong_role]["key_id"]
                resign(pack, trust, record_signers={field: wrong_role})
                self.assert_both(pack, trust)

    def test_trust_roles_require_distinct_ids_and_decoded_keys(self):
        pack, trust = self.fresh()
        trust["roles"]["observer"]["public_key"] = trust["roles"]["producer"]["public_key"]
        resign(pack, trust, record_signers={"observer_receipt": "producer"})
        self.assert_both(pack, trust)

        pack, trust = self.fresh()
        trust["roles"]["observer"]["key_id"] = trust["roles"]["producer"]["key_id"]
        pack["observer_receipt"]["key_id"] = trust["roles"]["producer"]["key_id"]
        resign(pack, trust)
        self.assert_both(pack, trust)

        pack, trust = self.fresh()
        trust["roles"]["producer"], trust["roles"]["observer"] = (
            trust["roles"]["observer"], trust["roles"]["producer"]
        )
        self.assert_both(pack, trust)

    def test_canonical_base64_not_just_decodable_bytes(self):
        for field in ("public_key", "signature"):
            for mutation in ("pad-bits", "missing-padding", "newline"):
                with self.subTest(field=field, mutation=mutation):
                    pack, trust = self.fresh()
                    target = (
                        trust["roles"]["producer"]
                        if field == "public_key" else pack["events"][0]
                    )
                    original = target[field]
                    if mutation == "pad-bits":
                        target[field] = nonzero_pad_bits(original)
                    elif mutation == "missing-padding":
                        target[field] = original.rstrip("=")
                    else:
                        target[field] = original + "\n"
                    if field == "signature":
                        # Preserve the modified signature text, but bind its new
                        # leaf bytes in the tree and all signed receipts.
                        bind_records(pack, trust)
                    self.assert_both(pack, trust)

    def test_real_calendar_dates_and_inclusive_time_bounds(self):
        for date, expected in (
            ("2024-02-29", "PASS"),
            ("2025-02-29", "FAIL"),
            ("2026-02-30", "FAIL"),
            ("0000-01-01", "FAIL"),
        ):
            with self.subTest(date=date):
                pack, trust = self.fresh()
                # Equal endpoints and equal adjacent timestamps are allowed.
                timestamp = date + "T12:00:00Z"
                pack["scope"]["window_start"] = timestamp
                pack["scope"]["window_end"] = timestamp
                for event in pack["events"]:
                    event["timestamp"] = timestamp
                for field in RECORD_ROLES:
                    pack[field]["issued_at"] = timestamp
                resign(pack, trust)
                self.assert_both(pack, trust, expected)

    def test_signed_receipt_count_and_issuance_boundaries(self):
        for field in RECORD_ROLES:
            with self.subTest(field=field, failure="count"):
                pack, trust = self.fresh()
                pack[field]["event_count"] = len(pack["events"]) + 1
                resign_record(pack, field, RECORD_ROLES[field])
                self.assert_both(pack, trust)
            with self.subTest(field=field, failure="issued-before-window-end"):
                pack, trust = self.fresh()
                pack[field]["issued_at"] = "0001-01-01T00:00:00Z"
                resign_record(pack, field, RECORD_ROLES[field])
                self.assert_both(pack, trust)

    def test_signed_event_references_and_attempt_order(self):
        for name in ("duplicate-id", "chain", "policy", "outcome-first"):
            with self.subTest(failure=name):
                pack, trust = self.fresh()
                if name == "duplicate-id":
                    pack["events"][1]["event_id"] = pack["events"][0]["event_id"]
                elif name == "chain":
                    pack["events"][0]["chain_id"] = pack["scope"]["chain_id"] + "-other"
                elif name == "policy":
                    pack["events"][0]["policy_id"] = pack["scope"]["policy_id"] + "-other"
                else:
                    first = next(
                        event for event in pack["events"]
                        if event["event_type"] == "AI_DECISION_ATTEMPT"
                    )
                    outcome = next(
                        event for event in pack["events"]
                        if event["event_type"] == "AI_DECISION_OUTCOME"
                        and event["provenance"]["attempt_id"] == first["provenance"]["attempt_id"]
                    )
                    pack["events"].remove(outcome)
                    pack["events"].insert(0, outcome)
                    for index, event in enumerate(pack["events"], 1):
                        event["sequence_no"] = index
                        event["timestamp"] = pack["scope"]["window_start"]
                resign(pack, trust)
                self.assert_both(pack, trust)

    def test_missing_external_trust_is_cli_error(self):
        with tempfile.TemporaryDirectory(prefix="vap-demo-usage-") as temporary:
            pack_path = Path(temporary) / "pack.json"
            pack_path.write_bytes(self.fixture_bytes["valid-pack.json"])
            for command in (
                [sys.executable, str(DEMO_DIR / "verify_python.py")],
                [self.node, str(self.node_script)],
            ):
                with self.subTest(runtime=command[0]):
                    completed = subprocess.run(
                        command + [str(pack_path), "--json"],
                        capture_output=True, text=True, timeout=20, check=False,
                    )
                    self.assertEqual(
                        completed.returncode, 2,
                        f"stdout={completed.stdout[:2000]!r}; stderr={completed.stderr[:2000]!r}",
                    )


if __name__ == "__main__":
    unittest.main()
