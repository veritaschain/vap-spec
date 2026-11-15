"""Reject weak caller-selected keys before attributing an incident statement."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fixture_transfer_erasure import build
from incident_assessor.assess import assess
from incident_assessor.model import InputError, configured_public_key

SMALL_ORDER_KEYS = (
    "0100000000000000000000000000000000000000000000000000000000000000",
    "ecffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff7f",
    "0000000000000000000000000000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000000000000000000000000080",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc05",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc85",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac037a",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac03fa",
)


class ConfiguredKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = build()["ER-03"]

    def provider(self):
        package, trust = copy.deepcopy(self.fixture)
        key_id = next(k for k, key in trust["keys"].items() if "provider" in key["roles"])
        return package, trust, key_id

    def test_all_eight_small_order_keys_are_rejected(self):
        for point in SMALL_ORDER_KEYS:
            with self.subTest(point=point):
                package, trust, key_id = self.provider()
                trust["keys"][key_id]["public_key"] = point
                with self.assertRaisesRegex(InputError, "Small-order configured Ed25519"):
                    assess(package, trust, allow_synthetic=True)

    def test_noncanonical_encodings_cannot_bypass_the_guard(self):
        p = 2**255 - 19
        values = [y | (sign << 255) for y in range(p, 2**255) for sign in (0, 1)]
        values += [y | (1 << 255) for y in (1, p - 1)]
        for value in values:
            with self.subTest(value=value):
                package, trust, key_id = self.provider()
                trust["keys"][key_id]["public_key"] = value.to_bytes(32, "little").hex()
                with self.assertRaisesRegex(InputError, "Noncanonical configured Ed25519"):
                    assess(package, trust, allow_synthetic=True)

    def test_forged_provider_attestation_cannot_become_verified(self):
        package, trust, key_id = self.provider()
        trust["keys"][key_id]["public_key"] = SMALL_ORDER_KEYS[0]
        for record in package["records"]:
            if record["key_id"] == key_id:
                record["signature"] = "01" + "00" * 63
        with self.assertRaisesRegex(InputError, "Small-order configured Ed25519"):
            assess(package, trust, allow_synthetic=True)

    def test_record_cannot_replace_an_existing_strong_trust_key(self):
        package, trust, key_id = self.provider()
        provider_ids = []
        for record in package["records"]:
            if record["key_id"] == key_id:
                record["signature"] = "01" + "00" * 63
                provider_ids.append(record["body"]["record_id"])
        report = assess(package, trust, allow_synthetic=True)
        for check in report["evidence_checks"]:
            if check["record_id"] in provider_ids:
                self.assertEqual(check["signature"], "FAILED")
                self.assertEqual(check["eligibility"], "INELIGIBLE")
        self.assertEqual(report["evidence_integrity"], "FAILED")

    def test_rejection_covers_unused_configured_key(self):
        package, trust, key_id = self.provider()
        package["records"] = []
        trust["keys"][key_id]["public_key"] = SMALL_ORDER_KEYS[0]
        with self.assertRaisesRegex(InputError, "Small-order configured Ed25519"):
            assess(package, trust, allow_synthetic=True)

    def test_malformed_key_encoding_is_an_input_error(self):
        for value in (None, [], 1, "00" * 31, "00" * 33, "11 " * 32):
            with self.subTest(value=value):
                with self.assertRaises(InputError):
                    configured_public_key(value)


if __name__ == "__main__":
    unittest.main()
