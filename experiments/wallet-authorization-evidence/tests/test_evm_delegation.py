"""Observe EIP-7702 state in a real, in-memory Prague EVM.

These tests use eth-tester's public development keys and locally deployed bytecode.
They do not contact a public chain, recreate an incident, or establish the safety of
a production wallet. Install requirements-evm.txt explicitly; missing dependencies
are an error, never a silently skipped behavior check.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

import rlp
from eth_account import Account
from eth_hash.auto import keccak
from eth_tester import EthereumTester, PyEVMBackend

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fixtures import make_fixture, rebind_fixture
from wallet_evidence import canonical_json, verify_bundle


ZERO_ADDRESS = "0x" + "00" * 20
# Increment storage slot zero, then STOP. No calls, transfers, or embedded addresses.
COUNTER_RUNTIME = bytes.fromhex("60005460010160005500")
REVERT_RUNTIME = bytes.fromhex("60006000fd")


class LocalDelegationTests(unittest.TestCase):
    def setUp(self):
        self.chain = EthereumTester(backend=PyEVMBackend())
        self.sponsor, self.authority, self.recipient = self.chain.get_accounts()[:3]
        self.chain_id = self.chain.backend.chain.chain_id
        self.target = self.deploy(COUNTER_RUNTIME)
        self.authorization_records = {}

    def deploy(self, runtime):
        # Twelve-byte creation prefix returns exactly the supplied short runtime.
        if not 0 < len(runtime) < 256:
            raise ValueError("This test helper supports short runtime code only")
        init = bytes([
            0x60, len(runtime), 0x60, 0x0C, 0x60, 0, 0x39,
            0x60, len(runtime), 0x60, 0, 0xF3,
        ]) + runtime
        tx_hash = self.chain.send_transaction({
            "from": self.sponsor, "gas": 500_000, "data": "0x" + init.hex(),
        })
        receipt = self.chain.get_transaction_receipt(tx_hash)
        self.assertEqual(receipt["status"], 1)
        target = receipt["contract_address"]
        self.assertEqual(self.chain.get_code(target), "0x" + runtime.hex())
        return target

    def authorize(self, target, *, nonce=None, chain_id=None, call_to=None):
        authority_nonce = self.chain.get_nonce(self.authority) if nonce is None else nonce
        authorization_chain = self.chain_id if chain_id is None else chain_id
        auth = Account.sign_authorization({
            "chainId": authorization_chain,
            "address": target,
            "nonce": authority_nonce,
        }, self.chain.backend.account_keys[1].to_bytes())
        # These are the actual EIP-7702 authorization signing bytes. The tuple
        # itself does not bind an application amount, destination or expiry.
        authorization_payload = b"\x05" + rlp.encode([
            authorization_chain, bytes.fromhex(target[2:]), authority_nonce,
        ])
        self.assertEqual(keccak(authorization_payload), auth.authorization_hash)
        transaction = {
            "type": 4,
            "chainId": self.chain_id,
            "nonce": self.chain.get_nonce(self.sponsor),
            "gas": 300_000,
            "maxFeePerGas": 2_000_000_000,
            "maxPriorityFeePerGas": 1_000_000_000,
            "to": self.authority if call_to is None else call_to,
            "value": 0,
            "data": "0x",
            "authorizationList": [auth],
        }
        signed = Account.sign_transaction(
            transaction, self.chain.backend.account_keys[0].to_bytes(),
        )
        tx_hash = self.chain.send_raw_transaction("0x" + signed.raw_transaction.hex())
        self.assertEqual(tx_hash, "0x" + signed.hash.hex())
        self.authorization_records[tx_hash] = {
            "payload": authorization_payload, "nonce": authority_nonce,
            "target": target.lower(), "chain_id": authorization_chain,
        }
        return self.chain.get_transaction_receipt(tx_hash)

    def delegation_code(self, target=None):
        return "0xef0100" + (self.target if target is None else target)[2:].lower()

    def slot_zero(self):
        return int(self.chain.get_storage_at(self.authority, "0x0"), 16)

    def evidence_report(self, receipt, *, clear=False, target=None):
        """Bind actual local EVM observations to synthetic authority statements.

        The observer keys, approval, policy and control evidence remain synthetic.
        This adapter is a first-party test harness, not an independent observer.
        Observation and evaluation times are illustrative clocks derived from the
        local block timestamp, not independently measured collection timestamps.
        """
        authorization = self.authorization_records[receipt["transaction_hash"]]
        # Derive the observed tuple fields from the actual signing bytes retained
        # for this receipt, independently of the caller's intended target/action.
        payload = authorization["payload"]
        if payload[:1] != b"\x05":
            raise ValueError("Expected EIP-7702 authorization signing bytes")
        tuple_chain, tuple_target, tuple_nonce = rlp.decode(payload[1:])
        observed_chain = int.from_bytes(tuple_chain, "big")
        observed_nonce = int.from_bytes(tuple_nonce, "big")
        if len(tuple_target) != 20 or rlp.encode([observed_chain, tuple_target, observed_nonce]) != payload[1:]:
            raise ValueError("Expected a canonical EIP-7702 authorization tuple")
        observed_target = "0x" + tuple_target.hex()
        if observed_chain != self.chain_id:
            raise ValueError("The evidence adapter only supports chain-specific authorizations")
        self.assertEqual(receipt, self.chain.get_transaction_receipt(receipt["transaction_hash"]))
        block = self.chain.get_block_by_number(receipt["block_number"])
        at = block["timestamp"] + 1
        bundle, trust, _ = make_fixture("clear_observed" if clear else "authorized", at=at)
        delegation_target = ZERO_ADDRESS if clear else (target or self.target).lower()
        rebind_fixture(bundle,
            operation_updates={
                "chain_id": str(self.chain_id), "wallet": self.authority.lower(),
                "destination": self.authority.lower(),
                "delegation_target": delegation_target,
                "nonce": str(observed_nonce),
            },
            policy_updates={
                "allowed_chains": [str(self.chain_id)],
                "allowed_wallets": [self.authority.lower()],
                "allowed_destinations": [self.authority.lower()],
                "allowed_delegation_targets": list(dict.fromkeys([delegation_target, ZERO_ADDRESS])),
            },
            execution_updates={
                "signing_payload": "0x" + payload.hex(),
                # The tuple does not encode application identity, amount or
                # destination. Those fields remain synthetic fixture context.
                "actual_operation_updates": {
                    "chain_id": str(observed_chain), "nonce": str(observed_nonce),
                    "delegation_target": observed_target,
                    "action": "clear_delegation" if observed_target == ZERO_ADDRESS else "delegate",
                },
            },
            chain_updates={
                "block_number": str(block["number"]), "block_hash": block["hash"],
                "transaction_hash": receipt["transaction_hash"],
                "transaction_block_number": str(receipt["block_number"]),
                "transaction_block_hash": receipt["block_hash"],
                "receipt_status": "success" if receipt["status"] == 1 else "reverted",
                "delegation_code": self.chain.get_code(self.authority, receipt["block_number"]),
                "finality": "observed_block", "observed_at": block["timestamp"],
            })
        return verify_bundle(bundle, trust, evaluation_time=at)

    def test_delegation_executes_again_without_a_new_authorization(self):
        receipt = self.authorize(self.target)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())
        self.assertEqual(self.slot_zero(), 1)
        later_hash = self.chain.send_transaction({
            "from": self.sponsor, "to": self.authority, "gas": 100_000,
        })
        self.assertEqual(self.chain.get_transaction_receipt(later_hash)["status"], 1)
        self.assertEqual(self.slot_zero(), 2)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())

    def test_valid_zero_address_authorization_clears_actual_code(self):
        self.authorize(self.target)
        nonce_before = self.chain.get_nonce(self.authority)
        receipt = self.authorize(ZERO_ADDRESS)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), "0x")
        self.assertEqual(self.chain.get_nonce(self.authority), nonce_before + 1)
        self.assertEqual(self.slot_zero(), 1)
        # Clearing delegation does not erase pre-existing storage.
        self.chain.send_transaction({
            "from": self.sponsor, "to": self.authority, "gas": 100_000,
        })
        self.assertEqual(self.slot_zero(), 1)

    def test_successful_receipt_can_skip_a_stale_clear_authorization(self):
        self.authorize(self.target)
        stale_nonce = self.chain.get_nonce(self.authority) - 1
        receipt = self.authorize(ZERO_ADDRESS, nonce=stale_nonce)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())
        self.assertEqual(self.slot_zero(), 2)

    def test_reverted_execution_does_not_undo_delegation(self):
        reverting_target = self.deploy(REVERT_RUNTIME)
        nonce_before = self.chain.get_nonce(self.authority)
        receipt = self.authorize(reverting_target)
        self.assertEqual(receipt["status"], 0)
        self.assertEqual(
            self.chain.get_code(self.authority), self.delegation_code(reverting_target),
        )
        self.assertEqual(self.chain.get_nonce(self.authority), nonce_before + 1)

    def test_nonce_advance_alone_does_not_clear_delegation(self):
        self.authorize(self.target)
        nonce_before = self.chain.get_nonce(self.authority)
        tx_hash = self.chain.send_transaction({
            "from": self.authority, "to": self.recipient, "gas": 21_000, "value": 0,
        })
        self.assertEqual(self.chain.get_transaction_receipt(tx_hash)["status"], 1)
        self.assertEqual(self.chain.get_nonce(self.authority), nonce_before + 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())

    def test_wrong_chain_authorization_is_skipped_even_with_success_receipt(self):
        nonce_before = self.chain.get_nonce(self.authority)
        receipt = self.authorize(self.target, chain_id=self.chain_id + 1)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), "0x")
        self.assertEqual(self.chain.get_nonce(self.authority), nonce_before)
        self.assertEqual(self.slot_zero(), 0)

    def test_zero_chain_id_authorization_accepts_matching_nonce_on_local_chain(self):
        receipt = self.authorize(self.target, chain_id=0)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())
        self.assertEqual(self.slot_zero(), 1)
        # This is one chain observation, not evidence about every other chain.

    def test_clear_persists_even_when_the_enclosing_execution_reverts(self):
        self.authorize(self.target)
        reverting_target = self.deploy(REVERT_RUNTIME)
        receipt = self.authorize(ZERO_ADDRESS, call_to=reverting_target)
        self.assertEqual(receipt["status"], 0)
        self.assertEqual(self.chain.get_code(self.authority), "0x")

    def test_actual_clear_observation_is_accepted_by_evidence_verifier(self):
        self.authorize(self.target)
        receipt = self.authorize(ZERO_ADDRESS)
        report = self.evidence_report(receipt, clear=True)
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["delegation_state"]["verdict"], "VALID")
        self.assertEqual(report["admission"], "ALLOW")  # Evidence only; executes nothing.

    def test_actual_matching_delegate_observation_is_accepted(self):
        receipt = self.authorize(self.target)
        report = self.evidence_report(receipt)
        self.assertTrue(all(claim["verdict"] == "VALID" for claim in report["claims"].values()))
        self.assertEqual(report["admission"], "ALLOW")  # Evidence only; executes nothing.

    def assert_observed_intent_mismatch(self, receipt, *, clear=False, actual_target, actual_nonce=None):
        with mock.patch(__name__ + ".verify_bundle", wraps=verify_bundle) as checked:
            report = self.evidence_report(receipt, clear=clear)
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["authorization"]["verdict"], "VALID")
        # A prior matching state can remain after the mismatched tuple is skipped.
        # The state observation is correct; execution/intent equality is not.
        self.assertEqual(report["claims"]["delegation_state"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")
        self.assertIn("execution:actual_operation_mismatch",
                      report["claims"]["execution_match"]["reasons"])
        self.assertEqual(report["admission"], "DENY")
        bundle = checked.call_args.args[0]
        actual = bundle["evidence"]["execution"]["payload"]["actual_operation"]
        self.assertEqual(actual["delegation_target"], actual_target.lower())
        self.assertEqual(actual["action"],
                         "clear_delegation" if actual_target == ZERO_ADDRESS else "delegate")
        self.assertEqual(actual["chain_id"], str(self.chain_id))
        if actual_nonce is not None:
            self.assertEqual(actual["nonce"], str(actual_nonce))
        self.assertNotEqual(actual["delegation_target"], bundle["operation"]["delegation_target"])

    def test_signed_bytes_override_cached_target_and_nonce_metadata(self):
        self.authorize(self.target)
        other_target = self.deploy(REVERT_RUNTIME)
        stale = self.chain.get_nonce(self.authority) - 1
        receipt = self.authorize(other_target, nonce=stale)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())
        # Cached helper metadata must not relabel the signed B tuple as A or
        # change the nonce in the observation derived from those signed bytes.
        record = self.authorization_records[receipt["transaction_hash"]]
        record.update(target=self.target.lower(), nonce=stale + 10)
        self.assert_observed_intent_mismatch(
            receipt, actual_target=other_target, actual_nonce=stale,
        )

    def test_actual_clear_tuple_cannot_be_reported_as_delegate(self):
        self.authorize(self.target)
        receipt = self.authorize(ZERO_ADDRESS, nonce=self.chain.get_nonce(self.authority) - 1)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())
        self.assert_observed_intent_mismatch(receipt, actual_target=ZERO_ADDRESS)

    def test_actual_delegate_tuple_cannot_be_reported_as_clear(self):
        receipt = self.authorize(self.target, nonce=self.chain.get_nonce(self.authority) + 1)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), "0x")
        self.assert_observed_intent_mismatch(receipt, clear=True, actual_target=self.target)

    def test_actual_stale_clear_cannot_be_replaced_by_success_receipt(self):
        self.authorize(self.target)
        receipt = self.authorize(ZERO_ADDRESS, nonce=self.chain.get_nonce(self.authority) - 1)
        self.assertEqual(receipt["status"], 1)
        report = self.evidence_report(receipt, clear=True)
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["delegation_state"]["verdict"], "INVALID")
        self.assertIn("chain:requested_delegation_state_contradicted",
                      report["claims"]["delegation_state"]["reasons"])
        self.assertEqual(report["admission"], "DENY")

    def test_actual_revert_does_not_negate_observed_delegation(self):
        reverting_target = self.deploy(REVERT_RUNTIME)
        receipt = self.authorize(reverting_target)
        self.assertEqual(receipt["status"], 0)
        report = self.evidence_report(receipt, target=reverting_target)
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["delegation_state"]["verdict"], "VALID")
        # This is a state assertion, not a claim that transaction execution succeeded.

    def test_signed_target_cannot_be_relabelled_as_requested_target(self):
        # The requested target remains A, while the stale signed tuple names B.
        # The EVM keeps A. The adapter must still report the signed B operation.
        self.authorize(self.target)
        alternate = self.deploy(REVERT_RUNTIME)
        stale = self.chain.get_nonce(self.authority) - 1
        receipt = self.authorize(alternate, nonce=stale)
        self.assertEqual(receipt["status"], 1)
        self.assertEqual(self.chain.get_code(self.authority), self.delegation_code())
        self.assert_observed_intent_mismatch(
            receipt, actual_target=alternate, actual_nonce=stale,
        )

    def test_receipt_retains_its_own_authorization_binding(self):
        first_receipt = self.authorize(self.target)
        first_report = self.evidence_report(first_receipt)
        self.authorize(self.target)
        # A later authorization has a different nonce and signing payload. An
        # older receipt must still use its own payload and historical block state.
        replayed_report = self.evidence_report(first_receipt)
        self.assertEqual(canonical_json(first_report), canonical_json(replayed_report))
        self.assertEqual(
            self.authorization_records[first_receipt["transaction_hash"]]["nonce"], 0,
        )


if __name__ == "__main__":
    unittest.main()
