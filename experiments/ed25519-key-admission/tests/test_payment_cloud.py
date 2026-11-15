"""Public entry-point regressions for experimental payment/cloud trust keys.

All keys, evidence, files and loopback services are synthetic. The weak-key
precondition is caller adoption; an input envelope cannot replace a strong pin.
No frozen vectors, distribution sources or recorded artifacts are imported.
"""
from __future__ import annotations

import copy
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

EXPERIMENTS = Path(__file__).resolve().parents[2]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, EXPERIMENTS / relative)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


payment = module("payment_evidence", "payment-api-evidence/payment_evidence.py")
payment_fixtures = module("_key_test_payment_fixtures", "payment-api-evidence/fixtures.py")
wallet = module("wallet_evidence", "wallet-authorization-evidence/wallet_evidence.py")
wallet_fixtures = module("_key_test_wallet_fixtures", "wallet-authorization-evidence/fixtures.py")
cloud = module("cloud_evidence", "cloud-credential-evidence/cloud_evidence.py")
cloud_fixtures = module("_key_test_cloud_fixtures", "cloud-credential-evidence/fixtures.py")
runtime = module("payment_runtime", "payment-runtime-pilot/payment_runtime.py")
authorization = module("authorization_gate", "payment-authorization-pilot/authorization_gate.py")
authorization_support = module("_key_test_authorization_support",
    "payment-authorization-pilot/tests/authorization_support.py")
collector = module("payment_collector", "payment-collector-pilot/payment_collector.py")
cloud_collector = module("_key_test_cloud_collector", "cloud-credential-collector/collector.py")
cloud_support = module("_key_test_cloud_support", "cloud-credential-collector/tests/collector_support.py")
pack = module("custody_pack", "cloud-credential-collector/custody_pack.py")

# Independent encodings: do not obtain the rejection set from the implementation.
SMALL_ORDER = tuple(bytes.fromhex(value) for value in (
    "0100000000000000000000000000000000000000000000000000000000000000",
    "ecffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff7f",
    "0000000000000000000000000000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000000000000000000000000080",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc05",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc85",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac037a",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac03fa",
))
FIELD = 2**255 - 19
NONCANONICAL = tuple((y | sign << 255).to_bytes(32, "little")
    for y in range(FIELD, 2**255) for sign in (0, 1)) + tuple(
    (y | 1 << 255).to_bytes(32, "little") for y in (1, FIELD - 1))
BAD_KEYS = SMALL_ORDER + NONCANONICAL
IDENTITY = SMALL_ORDER[0]
FORGED_SIGNATURE = (IDENTITY + bytes(32)).hex()
# Public synthetic seed; never use it for real evidence or service identity.
PRIVATE = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
PUBLIC = PRIVATE.public_key().public_bytes_raw()


class EncodingControls(unittest.TestCase):
    def test_eight_vectors_are_distinct_points_annihilated_by_eight(self):
        """Independent curve arithmetic checks the test data, not the guard."""
        d = -121665 * pow(121666, -1, FIELD) % FIELD

        def decode(raw):
            encoded = int.from_bytes(raw, "little")
            y, sign = encoded & (2**255 - 1), encoded >> 255
            self.assertLess(y, FIELD)
            square = (y * y - 1) * pow(d * y * y + 1, -1, FIELD) % FIELD
            x = pow(square, (FIELD + 3) // 8, FIELD)
            if x * x % FIELD != square:
                x = x * pow(2, (FIELD - 1) // 4, FIELD) % FIELD
            self.assertEqual(x * x % FIELD, square)
            if x % 2 != sign:
                x = -x % FIELD
            self.assertEqual(x % 2, sign)
            return x, y

        def add(a, b):
            x, y = a
            u, v = b
            product = d * x * u * y * v % FIELD
            return ((x * v + y * u) * pow(1 + product, -1, FIELD) % FIELD,
                    (y * v + x * u) * pow(1 - product, -1, FIELD) % FIELD)

        decoded = {decode(raw) for raw in SMALL_ORDER}
        self.assertEqual(len(decoded), 8)
        for point in decoded:
            for _ in range(3):
                point = add(point, point)
            self.assertEqual(point, (0, 1))
        self.assertEqual(len(set(NONCANONICAL)), 40)


class OfflineEvidenceTests(unittest.TestCase):
    def evaluate(self, target, *, public=None, forged=False, unused=False):
        if target == "cloud":
            case = cloud_fixtures.positive_case()
            key_id = cloud_fixtures.KEY_IDS["collector"]
            if public is not None:
                config = copy.deepcopy(case["trust"]["keys"][key_id])
                config["public_key"] = public.hex()
                case["trust"]["keys"]["unused" if unused else key_id] = config
            original = cloud_fixtures.sign_payload

            def sign(payload, role, **options):
                envelope = original(payload, role, **options)
                if forged and role == "collector":
                    envelope["signature"] = FORGED_SIGNATURE
                return envelope

            with mock.patch.object(cloud_fixtures, "sign_payload", side_effect=sign):
                bundle = cloud_fixtures.seal_bundle(case)
            return cloud.verify_bundle(bundle, case["trust"], scope=case["scope"],
                                       evaluation_time=case["evaluation_time"])
        if target == "payment":
            bundle, trust, identities, at = payment_fixtures.make_fixture()
            core, slot, role = payment, "collector", "collector"
            options = {"identities": identities}
        else:
            bundle, trust, at = wallet_fixtures.make_fixture()
            core, slot, role = wallet, "chain_observation", "chain_observer"
            options = {}
        envelope = bundle["evidence"][slot]
        if public is not None:
            trust[role]["unused" if unused else envelope["key_id"]] = public
        if forged:
            envelope["signature"] = FORGED_SIGNATURE
        return core.verify_bundle(bundle, trust, evaluation_time=at, **options)

    def test_all_three_evidence_apis_reject_all_eight_small_order_keys(self):
        for target in ("payment", "wallet", "cloud"):
            for public in SMALL_ORDER:
                with self.subTest(target=target, public=public.hex()):
                    with self.assertRaisesRegex(ValueError, "small_order"):
                        self.evaluate(target, public=public)

    def test_all_three_evidence_apis_reject_all_40_noncanonical_keys(self):
        for target in ("payment", "wallet", "cloud"):
            for public in NONCANONICAL:
                with self.subTest(target=target, public=public.hex()):
                    with self.assertRaisesRegex(ValueError, "noncanonical"):
                        self.evaluate(target, public=public)

    def test_unreferenced_weak_trust_entries_are_rejected(self):
        for target in ("payment", "wallet", "cloud"):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "small_order"):
                self.evaluate(target, public=IDENTITY, unused=True)

    def test_previously_accepted_forged_evidence_is_rejected_at_trust_admission(self):
        for target in ("payment", "wallet", "cloud"):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "small_order"):
                self.evaluate(target, public=IDENTITY, forged=True)

    def test_strong_fixture_keys_retain_their_original_bounded_results(self):
        for target in ("payment", "wallet"):
            result = self.evaluate(target)
            self.assertTrue(all(claim["verdict"] == "VALID" for claim in result["claims"].values()))
        self.assertEqual(self.evaluate("wallet")["admission"], "ALLOW")
        result = self.evaluate("cloud")
        self.assertEqual(result["claims"]["integrity"]["status"], "supported")
        self.assertEqual(result["claims"]["global_containment"]["status"], "unresolved")

    def test_existing_strong_pins_reject_the_same_forged_signatures(self):
        for target in ("payment", "wallet"):
            self.assertEqual(self.evaluate(target, forged=True)["claims"]["integrity"]["verdict"], "INVALID")
        self.assertEqual(self.evaluate("cloud", forged=True)["claims"]["integrity"]["status"], "contradicted")


class PaymentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.h = authorization_support.Harness(start=False)
        self.addCleanup(self.h.close)
        self.raw_request = runtime.request_bytes(self.h.request)
        self.receipt_payload = {
            "schema": runtime.RECEIPT_SCHEMA, "provider_id": runtime.DEFAULT_PROVIDER_ID,
            "request_digest": runtime.bytes_digest(self.raw_request), "request": self.h.request,
            "status": "settled", "failure_reason": None,
            "effect_id": runtime.bytes_digest(self.raw_request), "recorded_at_ms": 1,
        }
        self.receipt = self.envelope(self.receipt_payload, runtime.SIGNING_DOMAIN)
        self.package = collector.make_package(self.h.request, "provider_receipt", self.receipt)
        body = collector.load_json(self.package)
        self.ack_payload = {
            "schema": collector.ACK_SCHEMA, "collector_id": collector.DEFAULT_COLLECTOR_ID,
            "storage_epoch": 1, "recorded_at_ms": 1, "package_digest": collector.bytes_digest(self.package),
            **{field: body[field] for field in collector.BINDING_FIELDS},
        }
        self.nonce = "11" * 16

    def envelope(self, payload, domain, *, forged=False):
        signature = FORGED_SIGNATURE if forged else PRIVATE.sign(domain + runtime.canonical_json(payload)).hex()
        return runtime.canonical_json({"payload": payload, "signature": signature})

    def collector_messages(self, *, forged=False):
        ack = self.envelope(self.ack_payload, collector.SIGNING_DOMAIN, forged=forged)
        payload = {
            "schema": collector.READBACK_SCHEMA, "collector_id": collector.DEFAULT_COLLECTOR_ID,
            "recovery_epoch": 1, "nonce": self.nonce, "observed_at_ms": 1, "state": "PRESENT",
            "package_digest": collector.bytes_digest(self.package),
            "context_digest": collector.load_json(self.package)["context_digest"],
            "ack_digest": collector.bytes_digest(ack),
        }
        readback = self.envelope(payload, collector.SIGNING_DOMAIN, forged=forged)
        response = collector.canonical_json({"readback_bytes": readback.hex(),
            "ack_bytes": ack.hex(), "package_bytes": self.package.hex()})
        return ack, response

    def test_direct_receipt_ack_and_readback_reject_all_48_bad_keys(self):
        receipt = self.envelope(self.receipt_payload, runtime.SIGNING_DOMAIN, forged=True)
        ack, response = self.collector_messages(forged=True)
        for public in BAD_KEYS:
            for name, verify in (
                ("receipt", lambda: runtime.verify_receipt(receipt, self.raw_request, public)),
                ("ack", lambda: collector.verify_ack(ack, self.package, public)),
                ("readback", lambda: collector.verify_readback(response, self.package, public, nonce=self.nonce)),
            ):
                with self.subTest(entry=name, public=public.hex()):
                    with self.assertRaisesRegex(ValueError, "configured_ed25519_public_key"):
                        verify()

    def test_original_strong_receipt_ack_and_readback_still_verify(self):
        self.assertEqual(runtime.verify_receipt(self.receipt, self.raw_request, PUBLIC)["status"], "settled")
        ack, response = self.collector_messages()
        self.assertEqual(collector.verify_ack(ack, self.package, PUBLIC), self.ack_payload)
        self.assertEqual(collector.verify_readback(response, self.package, PUBLIC, nonce=self.nonce)["state"], "PRESENT")

    def test_same_forgeries_fail_under_existing_strong_pins(self):
        receipt = self.envelope(self.receipt_payload, runtime.SIGNING_DOMAIN, forged=True)
        ack, response = self.collector_messages(forged=True)
        for verify in (
            lambda: runtime.verify_receipt(receipt, self.raw_request, PUBLIC),
            lambda: collector.verify_ack(ack, self.package, PUBLIC),
            lambda: collector.verify_readback(response, self.package, PUBLIC, nonce=self.nonce),
        ):
            with self.assertRaisesRegex(ValueError, "signature"):
                verify()

    def test_runtime_constructor_rejects_before_creating_a_journal(self):
        for public in BAD_KEYS:
            with self.subTest(public=public.hex()):
                with self.assertRaisesRegex(ValueError, "configured_ed25519_public_key"):
                    self.h.adapter(endpoint="http://127.0.0.1:9", provider_public_key_hex=public.hex())
                self.assertFalse(self.h.journal_path.exists())

    def test_collector_constructor_rejects_all_bad_pins(self):
        for public in BAD_KEYS:
            with self.subTest(public=public.hex()), self.assertRaisesRegex(ValueError, "configured_ed25519_public_key"):
                collector.CollectorClient("http://127.0.0.1:9", self.h.context, public, self.h.credential)

    def test_authorization_constructor_rejects_every_role_and_unused_weak_key_before_io(self):
        for public in BAD_KEYS:
            for role in self.h.trust:
                for unused in (False, True):
                    trust = copy.deepcopy(self.h.trust)
                    key_id = "unused" if unused else next(iter(trust[role]))
                    trust[role][key_id] = public
                    with self.subTest(role=role, public=public.hex(), unused=unused):
                        with self.assertRaisesRegex(ValueError, "configured_ed25519_public_key"):
                            authorization.AuthorizedAdapter(object(), self.h.gate_config(trust=trust))
        self.assertFalse(self.h.journal_path.exists())

    def test_historical_record_with_forged_status_and_weak_recorded_trust_is_unverifiable(self):
        evidence = copy.deepcopy(self.h.evidence)
        envelope = authorization.load_json(evidence["final_status"])
        envelope["signature"] = FORGED_SIGNATURE
        evidence["final_status"] = authorization.canonical_json(envelope)
        trust = {role: {key_id: public.hex() for key_id, public in keys.items()}
                 for role, keys in self.h.trust.items()}
        trust["status_authority"][self.h.key_ids["final_status"]] = IDENTITY.hex()
        policy, identities = self.h.policy, self.h.identities
        # Construct the former accepted result independently, including every
        # digest affected by the newly fabricated signature/trust snapshot.
        decision = {
            "schema": authorization.DECISION_SCHEMA, "verdict": "AUTHORIZED",
            "request_digest": runtime.bytes_digest(self.raw_request),
            "evaluated_at_ms": self.h.at, "admitted_at_ms": self.h.at,
            "reasons": ["configured_mock_admission_supported_at_claim_time"],
            "policy_digest": authorization.digest(policy), "trust_manifest_digest": authorization.digest(trust),
            "identity_manifest_digest": authorization.digest(identities),
            "evidence_digests": {name: authorization.bytes_digest(raw) for name, raw in evidence.items()},
        }
        record = {
            "schema": authorization.PROOF_SCHEMA, "request_bytes": self.raw_request.hex(),
            "policy_bytes": authorization.canonical_json(policy).hex(),
            "trust_manifest_bytes": authorization.canonical_json(trust).hex(),
            "identity_manifest_bytes": authorization.canonical_json(identities).hex(),
            "max_status_age_ms": 30000, "evidence": {name: raw.hex() for name, raw in evidence.items()},
            "decision": decision,
        }
        result = authorization.recheck_record(authorization.canonical_json(record))
        self.assertEqual(result["verdict"], "UNVERIFIABLE")
        self.assertIsNone(result["decision"])


class LiveAdmissionTests(unittest.TestCase):
    def test_forged_status_cannot_reach_loopback_payment_under_weak_or_strong_config(self):
        h = authorization_support.Harness()
        self.addCleanup(h.close)
        evidence = copy.deepcopy(h.evidence)
        envelope = authorization.load_json(evidence["final_status"])
        envelope["signature"] = FORGED_SIGNATURE
        evidence["final_status"] = authorization.canonical_json(envelope)
        weak_trust = copy.deepcopy(h.trust)
        weak_trust["status_authority"][h.key_ids["final_status"]] = IDENTITY
        with self.assertRaisesRegex(ValueError, "small_order"):
            h.gate(trust=weak_trust)
        result = h.gate().submit(h.request, evidence)
        self.assertEqual(result["mock_admission"]["verdict"], "UNKNOWN")
        self.assertEqual(h.counts()["post_attempts"], 0)
        self.assertEqual(h.counts()["effects"], 0)
        # Valid synthetic signatures still authorize exactly one local effect.
        result = h.gate().submit(h.request, h.evidence)
        self.assertEqual(result["mock_admission"]["verdict"], "AUTHORIZED")
        self.assertEqual(result["state"], "SETTLED")
        self.assertEqual(h.counts()["effects"], 1)


class CloudCustodyTests(unittest.TestCase):
    def test_all_48_bad_pins_fail_before_store_or_package_processing(self):
        with tempfile.TemporaryDirectory() as temporary:
            absent = Path(temporary) / "not-created"
            for public in BAD_KEYS:
                with self.subTest(public=public.hex()):
                    with self.assertRaisesRegex(cloud_collector.CollectorError, "invalid_trusted_public_key"):
                        cloud_collector.Collector(absent, trusted_public_key=public)
                    with self.assertRaisesRegex(cloud_collector.CollectorError, "invalid_trusted_public_key"):
                        cloud_collector.initialize_store(absent, collector_id="test", key_id="test",
                            private_key=PRIVATE.private_bytes_raw(), trusted_public_key=public)
                    with self.assertRaisesRegex(pack.PackError, "invalid_trusted_public_key"):
                        pack.verify_pack({}, trusted_public_key=public, expected_store_id="aa" * 16)
                    self.assertFalse(absent.exists())

    def test_read_only_collector_rejects_forged_manifest_under_identity_pin(self):
        h = cloud_support.Harness()
        self.addCleanup(h.close)
        forged = copy.deepcopy(h.manifest)
        forged["signature"] = FORGED_SIGNATURE
        with closing(sqlite3.connect(h.db_path())) as connection:
            connection.execute("UPDATE metadata SET value=? WHERE key='manifest'",
                               (cloud_support.canonical(forged).decode(),))
            connection.commit()
        with self.assertRaisesRegex(cloud_collector.CollectorError, "invalid_trusted_public_key"):
            cloud_collector.Collector(h.store, trusted_public_key=IDENTITY)
        with self.assertRaisesRegex(cloud_collector.CollectorError, "custody_signature_mismatch"):
            cloud_collector.Collector(h.store, trusted_public_key=cloud_support.PUBLIC_TEST_KEY)

    def test_portable_pack_rejects_forged_chain_and_preserves_strong_control(self):
        h = cloud_support.Harness()
        self.addCleanup(h.close)
        h.collect("first")
        h.collect("same-bytes-second-receipt")
        output = h.root / "pack.json"
        expected_id = h.manifest["payload"]["store_id"]
        pack.export_pack(h.store, output, trusted_public_key=cloud_support.PUBLIC_TEST_KEY,
            private_key=cloud_support.PUBLIC_TEST_SEED, expected_store_id=expected_id)
        original = output.read_bytes()
        result = pack.verify_pack(original, trusted_public_key=cloud_support.PUBLIC_TEST_KEY,
                                  expected_store_id=expected_id)
        self.assertEqual((result["content_integrity"], result["receipt_count"], result["artifact_count"]),
                         ("supported", 2, 1))
        package = json.loads(original)
        package["manifest"]["signature"] = FORGED_SIGNATURE
        previous = None
        for envelope in package["receipts"]:
            envelope["payload"]["previous_receipt_sha256"] = previous
            envelope["signature"] = FORGED_SIGNATURE
            previous = cloud_support.digest(cloud_support.canonical(envelope))
        package["checkpoint"]["payload"]["receipt_sha256"] = previous
        package["checkpoint"]["signature"] = FORGED_SIGNATURE
        with self.assertRaisesRegex(pack.PackError, "invalid_trusted_public_key"):
            pack.verify_pack(package, trusted_public_key=IDENTITY, expected_store_id=expected_id)
        with self.assertRaisesRegex(pack.PackError, "custody_signature_mismatch"):
            pack.verify_pack(package, trusted_public_key=cloud_support.PUBLIC_TEST_KEY, expected_store_id=expected_id)
        self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
