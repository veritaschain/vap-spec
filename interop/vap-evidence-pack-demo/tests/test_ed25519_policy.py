"""Explicit Ed25519 input policy, separately from the frozen demo dataset.

These synthetic cases exercise both implementations. No original fixture or
historical result is rewritten. Torsion-point arithmetic below is test-only;
production verification remains with cryptography / Node's crypto library.
"""

import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from test_contract_boundaries import bind_records

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import verify_python as verifier

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
SMALL_ORDER_POINTS = (
    "0100000000000000000000000000000000000000000000000000000000000000",
    "ecffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff7f",
    "0000000000000000000000000000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000000000000000000000000080",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc05",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc85",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac037a",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac03fa",
)
ROLE_FIELDS = (
    ("event", None),
    ("producer_manifest", "producer"),
    ("observer_receipt", "observer"),
    ("demo_anchor_receipt", "anchor"),
)
NODE_BATCH = r"""
import fs from 'node:fs';
import { verifyPack, VerificationError } from './verify_node.mjs';
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
console.log(JSON.stringify(cases.map(({pack, trust}) => {
  try { return {checks: verifyPack(pack, trust), error: null}; }
  catch (error) {
    if (!(error instanceof VerificationError)) throw error;
    return {checks: [], error: error.message};
  }
})));
"""


def encoded(raw):
    return base64.b64encode(raw).decode("ascii")


def invalid_encodings():
    # Exactly 19 representable noncanonical y coordinates, each x sign.
    for y in range(P, 2**255):
        for sign in (0, 1):
            yield (y | (sign << 255)).to_bytes(32, "little")
    # x is zero for y = +1 and -1, so a set sign bit is not canonical.
    for y in (1, P - 1):
        yield (y | (1 << 255)).to_bytes(32, "little")


class Ed25519PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = verifier.load_json(HERE / "test-vectors/valid-pack.json")
        cls.trust = verifier.load_json(HERE / "test-vectors/demo-trust.json")

    def fresh(self):
        return copy.deepcopy(self.pack), copy.deepcopy(self.trust)

    def assert_cases(self, cases, expected_errors):
        result = subprocess.run(
            ["node", "--input-type=module", "-e", NODE_BATCH], cwd=HERE,
            input=json.dumps(cases), capture_output=True, text=True, timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        outputs = json.loads(result.stdout)
        self.assertEqual(len(outputs), len(cases))
        for index, (case, output, expected) in enumerate(zip(cases, outputs, expected_errors)):
            with self.subTest(index=index):
                with self.assertRaises(verifier.VerificationError) as caught:
                    verifier.verify_pack(case["pack"], case["trust"])
                self.assertEqual(str(caught.exception), expected)
                self.assertEqual(output, {"checks": [], "error": expected})

    def test_table_contains_all_eight_distinct_torsion_points(self):
        # Independent test-only decoding/doubling from RFC 8032 §§5.1.3–5.1.4.
        # Eight distinct solutions killed by 8 exhaust the cofactor-8 subgroup.
        d = (-121665 * pow(121666, -1, P)) % P
        root_minus_one = pow(2, (P - 1) // 4, P)
        decoded = set()
        for raw in map(bytes.fromhex, SMALL_ORDER_POINTS):
            integer = int.from_bytes(raw, "little")
            y, sign = integer & (2**255 - 1), integer >> 255
            xx = (y * y - 1) * pow(d * y * y + 1, -1, P) % P
            x = pow(xx, (P + 3) // 8, P)
            if x * x % P != xx:
                x = x * root_minus_one % P
            self.assertEqual(x * x % P, xx)
            if (x & 1) != sign:
                x = -x % P
            self.assertEqual(x & 1, sign)
            self.assertNotIn((x, y), decoded)
            decoded.add((x, y))
            for _ in range(3):
                product = d * x * x * y * y % P
                x, y = (
                    2 * x * y * pow(1 + product, -1, P) % P,
                    (y * y + x * x) * pow(1 - product, -1, P) % P,
                )
            self.assertEqual((x, y), (0, 1))
        self.assertEqual(len(decoded), 8)

    def test_every_small_order_key_is_rejected_for_each_role(self):
        cases, errors = [], []
        for role in ("producer", "observer", "anchor"):
            for point in SMALL_ORDER_POINTS:
                pack, trust = self.fresh()
                trust["roles"][role]["public_key"] = encoded(bytes.fromhex(point))
                cases.append({"pack": pack, "trust": trust})
                errors.append(f"trust.roles.{role}.public_key is a small-order Ed25519 point")
        self.assert_cases(cases, errors)

    def test_noncanonical_keys_cannot_bypass_the_point_policy(self):
        cases, errors = [], []
        for role in ("producer", "observer", "anchor"):
            for raw in invalid_encodings():
                pack, trust = self.fresh()
                trust["roles"][role]["public_key"] = encoded(raw)
                cases.append({"pack": pack, "trust": trust})
                errors.append(f"trust.roles.{role}.public_key has noncanonical Ed25519 point encoding")
        self.assert_cases(cases, errors)

    def signature_cases(self, raw_values, suffix):
        cases, errors = [], []
        for field, _role in ROLE_FIELDS:
            for raw in raw_values:
                pack, trust = self.fresh()
                record = pack["events"][0] if field == "event" else pack[field]
                record["signature"] = encoded(raw)
                if field == "event":
                    # Preserve the bad signature but rebuild all unrelated
                    # root/count/receipt integrity with the public TEST seeds.
                    bind_records(pack, trust)
                cases.append({"pack": pack, "trust": trust})
                errors.append(field + suffix)
        self.assert_cases(cases, errors)

    def test_small_order_r_with_zero_s_is_rejected_for_events_and_receipts(self):
        self.signature_cases(
            [bytes.fromhex(point) + bytes(32) for point in SMALL_ORDER_POINTS],
            " signature R is a small-order Ed25519 point",
        )

    def test_noncanonical_r_is_rejected_for_events_and_receipts(self):
        self.signature_cases(
            [point + bytes(32) for point in invalid_encodings()],
            " signature R has noncanonical Ed25519 point encoding",
        )

    def test_scalar_at_or_above_l_is_rejected_before_backend_verification(self):
        original = base64.b64decode(self.pack["events"][0]["signature"])
        self.signature_cases(
            [original[:32] + scalar.to_bytes(32, "little")
             for scalar in (L, L + 1, 2**256 - 1)],
            " signature scalar must be less than Ed25519 subgroup order",
        )

    def test_in_range_zero_and_l_minus_one_still_need_the_signature_equation(self):
        # S=0 is not independently forbidden by RFC 8032 or this policy.
        # These mutations are not valid signatures for their message/key.
        cases = []
        for scalar in (0, L - 1):
            pack, trust = self.fresh()
            record = pack["events"][0]
            signature = base64.b64decode(record["signature"])
            record["signature"] = encoded(signature[:32] + scalar.to_bytes(32, "little"))
            bind_records(pack, trust)
            cases.append({"pack": pack, "trust": trust})
            with self.assertRaisesRegex(verifier.VerificationError, "^event signature is invalid$"):
                verifier.verify_pack(pack, trust)
        result = subprocess.run(
            ["node", "--input-type=module", "-e", NODE_BATCH], cwd=HERE,
            input=json.dumps(cases), capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for output in json.loads(result.stdout):
            self.assertEqual(output["error"], "event signature does not match the supplied role key")

    def test_fixed_forged_pack_is_rejected_by_both_clis(self):
        directory = HERE / "security-vectors"
        manifest = json.loads((directory / "manifest.json").read_text())
        for name, record in manifest["files"].items():
            raw = (directory / name).read_bytes()
            self.assertEqual(len(raw), record["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["sha256"])
        for command in (
            [sys.executable, str(HERE / "verify_python.py")],
            ["node", str(HERE / "verify_node.mjs")],
        ):
            result = subprocess.run(
                command + [str(directory / "invalid-small-order-pack.json"),
                           "--trust", str(directory / "invalid-small-order-trust.json"), "--json"],
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output, {
                "contract_id": verifier.CONTRACT_ID, "verdict": "FAIL", "checks": [],
                "error": "trust.roles.producer.public_key is a small-order Ed25519 point",
            })

    def test_replacing_only_the_pack_does_not_replace_caller_trust(self):
        pack = verifier.load_json(HERE / "security-vectors/invalid-small-order-pack.json")
        # This negative control keeps the original independently selected keys.
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_pack(pack, self.trust)
        result = subprocess.run(
            ["node", "--input-type=module", "-e", NODE_BATCH], cwd=HERE,
            input=json.dumps([{"pack": pack, "trust": self.trust}]),
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(json.loads(result.stdout)[0]["error"])


if __name__ == "__main__":
    unittest.main()
