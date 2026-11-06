"""Live synthetic admission tests, using real native HTTP/SQLite effects.

Identity/role mappings and status assertions are controlled synthetic inputs.
These tests establish a scoped mock prerequisite, not real business approval,
current external revocation state, or a production authorization boundary.
"""
from __future__ import annotations

import copy
from contextlib import closing
from pathlib import Path
import signal
import sqlite3
import sys
import threading
from unittest import mock
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parent))
from authorization_support import Harness, authorization, runtime


class AuthorizationGateTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def rows(self):
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            return {
                "claims": db.execute("SELECT count(*) FROM dispatches").fetchone()[0],
                "proofs": db.execute("SELECT count(*) FROM authorization_proofs").fetchone()[0],
            }

    def assert_no_dispatch(self):
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(self.h.counts()["effects"], 0)
        self.assertEqual(self.rows(), {"claims": 0, "proofs": 0})

    def assert_one_effect(self):
        counts = self.h.counts()
        self.assertEqual(counts["post_attempts"], 1)
        self.assertEqual(counts["effects"], 1)
        self.assertEqual(counts["payments"], 1)
        self.assertEqual(int(counts["balances"]["source-A"]), 98750)
        self.assertEqual(int(counts["balances"]["beneficiary-A"]), 1250)
        self.assertEqual(self.rows(), {"claims": 1, "proofs": 1})

    def assert_blocked(self, gate, evidence, *, request=None, verdict=None):
        result = gate.submit(self.h.request if request is None else request, evidence)
        self.assertEqual(result["state"], "REJECTED")
        if verdict is not None:
            self.assertEqual(result["mock_admission"]["verdict"], verdict)
        else:
            self.assertNotEqual(result["mock_admission"]["verdict"], "AUTHORIZED")
        self.assert_no_dispatch()
        return result

    def test_healthy_admission_persists_original_evidence_and_same_time_as_native_claim(self):
        gate = self.h.gate()
        result = gate.submit(self.h.request, self.h.evidence)
        self.assertEqual(result["state"], "SETTLED")
        self.assertEqual(result["mock_admission"]["verdict"], "AUTHORIZED")
        self.assertIs(result["business_authorization_verified"], False)
        self.assertIs(result["automatic_retry"], False)
        self.assert_one_effect()
        proof = gate.read_authorization(self.h.request)
        self.assertEqual(proof["status"], "FOUND")
        self.assertEqual(proof["decision"]["verdict"], "AUTHORIZED")
        self.assertEqual(proof["record_digest"], authorization.bytes_digest(proof["record_bytes"]))
        saved = authorization.load_json(proof["record_bytes"])
        self.assertEqual(saved["evidence"], {name: raw.hex() for name, raw in self.h.evidence.items()})
        self.assertEqual(saved["max_status_age_ms"], 30000)
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            native_time = db.execute("SELECT claimed_at_ms FROM dispatches").fetchone()[0]
            proof_time = db.execute("SELECT admitted_at_ms FROM authorization_proofs").fetchone()[0]
        self.assertEqual(native_time, proof_time)
        self.assertEqual(native_time, proof["decision"]["admitted_at_ms"])
        self.assertEqual(proof["request_digest"], runtime.bytes_digest(runtime.request_bytes(self.h.request)))
        for secret in [self.h.credential, *(key.private_bytes_raw().hex() for key in self.h.signing_keys.values())]:
            self.assertNotIn(secret.encode(), proof["record_bytes"])
            self.assertNotIn(secret.encode().hex().encode(), proof["record_bytes"])

    def test_two_signing_keys_need_two_eligible_configured_people(self):
        maker = self.h.signing_keys["maker_approval"].public_key().public_bytes_raw().hex()
        checker = self.h.signing_keys["checker_approval"].public_key().public_bytes_raw().hex()
        self.assertNotEqual(maker, checker)
        for condition, verdict in (("same_person", "DENIED"), ("wrong_role", "DENIED"),
                                   ("wrong_scope", "DENIED"), ("missing_identity", "UNKNOWN")):
            with self.subTest(condition=condition):
                identities = copy.deepcopy(self.h.identities)
                if condition == "same_person":
                    identities[checker]["person_id"] = identities[maker]["person_id"]
                elif condition == "wrong_role":
                    identities[checker]["roles"] = ["maker"]
                elif condition == "wrong_scope":
                    identities[checker]["tenant"] = "another-tenant"
                else:
                    del identities[checker]
                self.assert_blocked(self.h.gate(identities=identities), self.h.evidence, verdict=verdict)

    def test_public_key_aliases_cannot_assign_two_different_people(self):
        evidence = copy.deepcopy(self.h.evidence)
        trust = copy.deepcopy(self.h.trust)
        identities = copy.deepcopy(self.h.identities)
        maker_key = self.h.signing_keys["maker_approval"]
        public = maker_key.public_key().public_bytes_raw()
        trust["approver"]["checker-alias-of-maker-key"] = public
        identities[public.hex()]["roles"] = ["maker", "checker"]
        payload = authorization.load_json(evidence["checker_approval"])["payload"]
        evidence["checker_approval"] = authorization.sign_evidence(payload, "checker-alias-of-maker-key", maker_key)
        self.h.refresh_status(evidence)
        self.assert_blocked(self.h.gate(trust=trust, identities=identities), evidence, verdict="DENIED")
        # The external person map is keyed by VERIFIED public bytes, not aliases.
        by_alias = {"maker-key-id": {**identities[public.hex()], "person_id": "person-one"},
                    "checker-key-id": {**identities[public.hex()], "person_id": "person-two"}}
        with self.assertRaises(ValueError):
            self.h.gate(trust=trust, identities=by_alias)
        self.assert_no_dispatch()

    def test_missing_signature_wrong_role_and_wrong_domain_are_not_authorization(self):
        for condition in ("missing", "tampered", "wrong_role", "wrong_domain", "unknown_key"):
            with self.subTest(condition=condition):
                evidence = copy.deepcopy(self.h.evidence)
                env = authorization.load_json(evidence["maker_approval"])
                if condition == "missing":
                    del evidence["maker_approval"]
                elif condition == "tampered":
                    env["payload"]["approval_id"] = "modified-after-signature"
                    evidence["maker_approval"] = authorization.canonical_json(env)
                elif condition == "wrong_role":
                    evidence["maker_approval"] = authorization.sign_evidence(
                        env["payload"], self.h.key_ids["final_status"], self.h.signing_keys["final_status"])
                elif condition == "unknown_key":
                    evidence["maker_approval"] = authorization.sign_evidence(
                        env["payload"], "unconfigured-approval-key", self.h.signing_keys["maker_approval"])
                else:
                    signed = {"key_id": env["key_id"], "payload": env["payload"]}
                    env["signature"] = self.h.signing_keys["maker_approval"].sign(
                        b"VSO experimental payment evidence v0\x00" + authorization.canonical_json(signed)).hex()
                    evidence["maker_approval"] = authorization.canonical_json(env)
                self.assert_blocked(self.h.gate(), evidence, verdict="UNKNOWN")

    def test_signed_approvals_cannot_be_used_for_changed_native_request(self):
        substitutions = {"amount_minor": "1251", "beneficiary": "beneficiary-B",
                         "operation_id": "different-operation", "idempotency_key": "different-key",
                         "tenant": "different-tenant", "environment": "different-environment",
                         "currency": "EUR", "minor_unit_scale": 3,
                         "configuration_digest": "sha256:" + "cd" * 32, "recovery_epoch": 2}
        for field, value in substitutions.items():
            with self.subTest(field=field):
                request = {**self.h.request, field: value}
                self.assert_blocked(self.h.gate(), self.h.evidence, request=request)

    def test_policy_constraints_apply_even_when_every_signature_binds_the_request(self):
        for updates in ({"max_amount_minor": "1249"}, {"allowed_beneficiaries": ["beneficiary-B"]},
                        {"allowed_sources": ["beneficiary-A"]},
                        {"valid_until_ms": self.h.at - 1}):
            with self.subTest(updates=updates):
                policy = {**copy.deepcopy(self.h.policy), **updates}
                evidence = self.h.make_evidence(self.h.request, policy=policy)
                self.assert_blocked(self.h.gate(policy=policy), evidence, verdict="DENIED")

    def test_expired_or_not_yet_valid_approvals_never_create_a_claim(self):
        for slot in authorization.APPROVALS:
            for condition in ("expired", "future"):
                with self.subTest(slot=slot, condition=condition):
                    evidence = copy.deepcopy(self.h.evidence)
                    if condition == "expired":
                        self.h.resign(evidence, slot, expires_at_ms=self.h.at - 1)
                    else:
                        self.h.resign(evidence, slot, issued_at_ms=self.h.at + 30000)
                    self.h.refresh_status(evidence)
                    # A future-dated assertion is not usable at admission;
                    # expiry is a contradiction in an already usable statement.
                    self.assert_blocked(self.h.gate(), evidence,
                                        verdict="DENIED" if condition == "expired" else "UNKNOWN")

    def test_identity_eligibility_must_cover_approval_issuance_and_admission(self):
        for condition in ("started_after_approval", "expired_before_admission"):
            with self.subTest(condition=condition):
                identities = copy.deepcopy(self.h.identities)
                checker = self.h.signing_keys["checker_approval"].public_key().public_bytes_raw().hex()
                if condition == "started_after_approval":
                    identities[checker]["valid_from_ms"] = self.h.at - 500
                else:
                    identities[checker]["valid_until_ms"] = self.h.at - 1
                self.assert_blocked(self.h.gate(identities=identities), self.h.evidence, verdict="DENIED")

    def test_status_must_be_supplied_authenticated_scoped_and_fresh(self):
        for condition, verdict in (("missing", "UNKNOWN"), ("stale", "UNKNOWN"),
                                   ("expired", "UNKNOWN"), ("revoked", "DENIED"),
                                   ("unknown", "UNKNOWN"), ("wrong_epoch", "DENIED"),
                                   ("wrong_approval", "DENIED")):
            with self.subTest(condition=condition):
                evidence = copy.deepcopy(self.h.evidence)
                if condition == "missing":
                    del evidence["final_status"]
                elif condition == "stale":
                    # Keep the temporal order coherent so only freshness fails.
                    for name in authorization.APPROVALS:
                        self.h.resign(evidence, name, issued_at_ms=self.h.at - 70000)
                    self.h.refresh_status(evidence)
                    self.h.resign(evidence, "final_status", observed_at_ms=self.h.at - 60000)
                elif condition == "expired":
                    self.h.resign(evidence, "final_status", valid_until_ms=self.h.at - 1)
                elif condition == "revoked":
                    self.h.resign(evidence, "final_status", state="revoked", revoked_at_ms=self.h.at - 100)
                elif condition == "unknown":
                    self.h.resign(evidence, "final_status", state="unknown")
                elif condition == "wrong_epoch":
                    self.h.resign(evidence, "final_status", recovery_epoch=99)
                else:
                    refs = authorization.load_json(evidence["final_status"])["payload"]["approval_digests"]
                    refs["maker_approval"] = "sha256:" + "ff" * 32
                    self.h.resign(evidence, "final_status", approval_digests=refs)
                self.assert_blocked(self.h.gate(), evidence, verdict=verdict)

    def test_admission_time_is_sampled_after_the_actual_claim_lock_is_acquired(self):
        # The client clock advances from a genuine past interval to present
        # while BEGIN IMMEDIATE waits on a real lock. The provider clock is
        # untouched, and no future execution observation is manufactured.
        for condition, verdict in (("approval_expired", "DENIED"), ("status_stale", "UNKNOWN")):
            with self.subTest(condition=condition):
                past = self.h.at - 60000
                evidence = self.h.make_evidence(self.h.request, at=past)
                for name in authorization.APPROVALS:
                    self.h.resign(evidence, name, expires_at_ms=(self.h.at - 1 if condition == "approval_expired"
                                                               else self.h.at + 60000))
                self.h.refresh_status(evidence)
                self.h.resign(evidence, "final_status", valid_until_ms=self.h.at + 60000)
                age = 120000 if condition == "approval_expired" else 30000
                native = self.h.adapter(sqlite_timeout=2.0)
                gate = self.h.gate(native=native, max_status_age_ms=age)
                attempted = threading.Event()
                results = []
                errors = []
                clock = {"at": past}
                present = authorization.now_ms()
                connect = runtime._connect

                def traced_connect(*args, **kwargs):
                    connection = connect(*args, **kwargs)
                    connection.set_trace_callback(
                        lambda statement: attempted.set() if statement == "BEGIN IMMEDIATE" else None)
                    return connection

                def submit():
                    try:
                        results.append(gate.submit(self.h.request, evidence))
                    except BaseException as exc:
                        errors.append(exc)

                with closing(sqlite3.connect(self.h.journal_path, timeout=0.1)) as locked:
                    locked.execute("BEGIN IMMEDIATE")
                    with mock.patch.object(runtime, "_connect", side_effect=traced_connect), \
                         mock.patch.object(runtime.time, "time_ns", side_effect=lambda: clock["at"] * 1000000):
                        worker = threading.Thread(target=submit)
                        worker.start()
                        try:
                            self.assertTrue(attempted.wait(timeout=2), "claim did not reach the native SQLite lock")
                            clock["at"] = present
                        finally:
                            locked.rollback()
                            worker.join(timeout=5)
                        self.assertFalse(worker.is_alive())
                self.assertEqual(errors, [])
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]["state"], "REJECTED")
                self.assertEqual(results[0]["mock_admission"]["verdict"], verdict)
                self.assertEqual(results[0]["mock_admission"]["evaluated_at_ms"], present)
                self.assertIsNone(results[0]["mock_admission"]["admitted_at_ms"])
                self.assert_no_dispatch()

    def test_actual_proof_store_failure_rolls_back_claim_and_prevents_post(self):
        gate = self.h.gate()
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            db.execute("""CREATE TRIGGER test_block_proof_store
                BEFORE INSERT ON authorization_proofs BEGIN
                SELECT RAISE(ABORT, 'trusted_test_proof_store_failure'); END""")
            db.commit()
        result = gate.submit(self.h.request, self.h.evidence)
        self.assertEqual(result["state"], "JOURNAL_UNAVAILABLE")
        self.assertEqual(result["mock_admission"]["verdict"], "UNKNOWN")
        self.assert_no_dispatch()
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            db.execute("DROP TRIGGER test_block_proof_store")
            db.commit()
        self.assertEqual(gate.submit(self.h.request, self.h.evidence)["state"], "SETTLED")
        self.assert_one_effect()

    def test_sigkill_during_proof_and_claim_transaction_leaves_neither_committed(self):
        gate = self.h.gate()
        worker = self.h.authorized_worker(barrier="after_authorization_proof")
        event = worker.event()
        self.assertEqual(event["stage"], "after_authorization_proof")
        self.assertEqual(worker.kill(), -signal.SIGKILL)
        self.assert_no_dispatch()
        # This controlled crash occurred before claim commit and before POST.
        self.assertEqual(gate.submit(self.h.request, self.h.evidence)["state"], "SETTLED")
        self.assert_one_effect()

    def test_sigkill_after_claim_retains_original_proof_and_never_resends(self):
        gate = self.h.gate()
        worker = self.h.authorized_worker(barrier="after_claim")
        self.assertEqual(worker.event()["stage"], "after_claim")
        self.assertEqual(self.rows(), {"claims": 1, "proofs": 1})
        original = gate.read_authorization(self.h.request)
        self.assertEqual(original["status"], "FOUND")
        self.assertEqual(worker.kill(), -signal.SIGKILL)
        revoked = copy.deepcopy(self.h.evidence)
        self.h.resign(revoked, "final_status", state="revoked", revoked_at_ms=self.h.at - 100)
        self.assertEqual(gate.submit(self.h.request, revoked)["state"], "UNKNOWN")
        self.assertEqual(gate.reconcile(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(gate.read_authorization(self.h.request)["record_bytes"], original["record_bytes"])
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(self.h.counts()["effects"], 0)
        self.assertEqual(self.h.counts()["lookup_attempts"], 1)

    def test_prior_unknown_payment_reconciles_without_fresh_authorization_or_resend(self):
        self.h.stop_provider()
        self.h.provider_config["drop_after_commit"] = True
        self.h.start_provider()
        gate = self.h.gate()
        first = gate.submit(self.h.request, self.h.evidence)
        self.assertEqual(first["state"], "UNKNOWN")
        original = gate.read_authorization(self.h.request)
        expired_policy = {**self.h.policy, "valid_until_ms": self.h.at - 1}
        later = self.h.gate(policy=expired_policy)
        revoked = copy.deepcopy(self.h.evidence)
        self.h.resign(revoked, "final_status", state="revoked", revoked_at_ms=self.h.at - 100)
        self.assertEqual(later.submit(self.h.request, revoked)["state"], "UNKNOWN")
        recovered = later.reconcile(self.h.request)
        self.assertEqual(recovered["state"], "SETTLED")
        self.assertEqual(recovered["mock_admission"]["verdict"], "AUTHORIZED")
        self.assertIs(recovered["mock_admission"]["historical_original_decision"], True)
        self.assertEqual(later.read_authorization(self.h.request)["record_bytes"], original["record_bytes"])
        self.assert_one_effect()
        self.assertEqual(self.h.counts()["lookup_attempts"], 1)

    def test_repeat_cannot_replace_the_original_approval_pack(self):
        gate = self.h.gate()
        gate.submit(self.h.request, self.h.evidence)
        original = gate.read_authorization(self.h.request)
        different = self.h.make_evidence(self.h.request, suffix="different-approvals")
        self.assertNotEqual(different["maker_approval"], self.h.evidence["maker_approval"])
        second = gate.submit(self.h.request, different)
        self.assertEqual(second["state"], "SETTLED")
        self.assertEqual(second["mock_admission"]["proof_digest"], original["record_digest"])
        self.assertEqual(gate.read_authorization(self.h.request)["record_bytes"], original["record_bytes"])
        self.assert_one_effect()

    def test_legacy_native_claim_is_not_backfilled_or_labeled_authorized(self):
        native = self.h.adapter()
        first = native.submit(self.h.request)
        self.assertEqual(first["state"], "SETTLED")
        gate = self.h.gate(native=native)
        repeat = gate.submit(self.h.request, self.h.evidence)
        self.assertEqual(repeat["state"], "SETTLED")
        self.assertEqual(repeat["mock_admission"]["verdict"], "UNKNOWN")
        self.assertEqual(gate.reconcile(self.h.request)["mock_admission"]["verdict"], "UNKNOWN")
        self.assertEqual(gate.read_authorization(self.h.request)["status"], "MISSING")
        self.assertEqual(self.rows(), {"claims": 1, "proofs": 0})
        self.assertEqual(self.h.counts()["post_attempts"], 1)
        self.assertEqual(self.h.counts()["effects"], 1)

    def test_concurrent_native_clients_preserve_one_winning_admission_proof(self):
        gate = self.h.gate()
        alternate = self.h.make_evidence(self.h.request, suffix="second-client")
        # Each subprocess repeats native and authorization-store initialization.
        # Start the claim race only after both have finished those transactions.
        options = {"barrier": "after_claim", "start_barrier": True,
                   "config_changes": {"sqlite_timeout": 2.0}}
        a = self.h.authorized_worker(evidence=self.h.evidence, **options)
        ready_a = a.event()
        self.assertEqual((ready_a["event"], ready_a["stage"]), ("ready", "initialized"))
        b = self.h.authorized_worker(evidence=alternate, **options)
        ready_b = b.event()
        self.assertEqual((ready_b["event"], ready_b["stage"]), ("ready", "initialized"))
        self.assertEqual(self.rows(), {"claims": 0, "proofs": 0})
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        a.release()
        b.release()
        events = [(a, a.event(), self.h.evidence), (b, b.event(), alternate)]
        winners = [(p, e, pack) for p, e, pack in events if e["event"] == "barrier"]
        followers = [(p, e) for p, e, _ in events if e["event"] == "result"]
        self.assertEqual(len(winners), 1)
        self.assertEqual(len(followers), 1)
        self.assertEqual(followers[0][1]["result"]["state"], "UNKNOWN")
        self.assertEqual(followers[0][1]["result"]["reason"], "durable_claim_outcome_unresolved")
        self.assertEqual(self.rows(), {"claims": 1, "proofs": 1})
        persisted = authorization.load_json(gate.read_authorization(self.h.request)["record_bytes"])
        self.assertEqual(persisted["evidence"], {name: raw.hex() for name, raw in winners[0][2].items()})
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        winners[0][0].release()
        self.assertEqual(winners[0][0].result()["state"], "SETTLED")
        self.assertEqual(followers[0][0].proc.wait(timeout=5), 0)
        self.assert_one_effect()

    def test_same_instance_concurrent_calls_own_their_request_and_approval_snapshots(self):
        native = self.h.adapter(sqlite_timeout=2.0)
        gate = self.h.gate(native=native)
        original_evidence = copy.deepcopy(self.h.evidence)
        caller_evidence = copy.deepcopy(original_evidence)
        other = {**self.h.request, "operation_id": "operation-B", "idempotency_key": "idempotency-B"}
        other_evidence = self.h.make_evidence(other, suffix="B")
        bad = authorization.load_json(other_evidence["checker_approval"])
        bad["payload"]["approval_id"] = "changed-without-resigning"
        other_evidence["checker_approval"] = authorization.canonical_json(bad)
        started = {name: threading.Event() for name in ("approval-A", "approval-B")}
        results, errors = {}, []
        connect = runtime._connect

        def traced_connect(*args, **kwargs):
            connection = connect(*args, **kwargs)
            name = threading.current_thread().name
            connection.set_trace_callback(lambda statement: started[name].set()
                                          if statement == "BEGIN IMMEDIATE" and name in started else None)
            return connection

        def submit(name, request, pack):
            try:
                results[name] = gate.submit(request, pack)
            except BaseException as exc:
                errors.append(exc)

        a = threading.Thread(name="approval-A", target=submit, args=("A", self.h.request, caller_evidence))
        b = threading.Thread(name="approval-B", target=submit, args=("B", other, other_evidence))
        with closing(sqlite3.connect(self.h.journal_path, timeout=0.1)) as locked:
            locked.execute("BEGIN IMMEDIATE")
            with mock.patch.object(runtime, "_connect", side_effect=traced_connect):
                a.start()
                try:
                    self.assertTrue(started["approval-A"].wait(timeout=2))
                    # The A call already owns its bytes. A later caller mutation
                    # and simultaneous B call must not swap the pending proof.
                    caller_evidence["maker_approval"] = other_evidence["maker_approval"]
                    b.start()
                    self.assertTrue(started["approval-B"].wait(timeout=2))
                finally:
                    locked.rollback()
                    a.join(timeout=5)
                    if b.ident is not None:
                        b.join(timeout=5)
                self.assertFalse(a.is_alive())
                self.assertFalse(b.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(results["A"]["state"], "SETTLED")
        self.assertEqual(results["B"]["state"], "REJECTED")
        self.assertEqual(results["B"]["mock_admission"]["verdict"], "UNKNOWN")
        proof = authorization.load_json(gate.read_authorization(self.h.request)["record_bytes"])
        self.assertEqual(proof["evidence"], {name: raw.hex() for name, raw in original_evidence.items()})
        self.assertEqual(gate.read_authorization(other)["status"], "MISSING")
        self.assert_one_effect()

    def test_reconciliation_and_status_cannot_attach_another_mutated_request_proof(self):
        self.h.stop_provider()
        self.h.provider_config["drop_after_commit"] = True
        self.h.start_provider()
        native = self.h.adapter()
        gate = self.h.gate(native=native)
        original = copy.deepcopy(self.h.request)
        other = {**self.h.request, "operation_id": "operation-B", "idempotency_key": "idempotency-B", "amount_minor": "500"}
        self.assertEqual(gate.submit(original, self.h.evidence)["state"], "UNKNOWN")
        self.assertEqual(gate.submit(other, self.h.make_evidence(other, suffix="B"))["state"], "UNKNOWN")
        original_proof = gate.read_authorization(original)
        other_proof = gate.read_authorization(other)
        self.assertNotEqual(original_proof["record_digest"], other_proof["record_digest"])
        self.assertEqual(gate.reconcile(other)["state"], "SETTLED")
        caller_request = copy.deepcopy(original)
        genuine_http = native._http

        def mutate_after_real_get(method, path, body=None):
            observed = genuine_http(method, path, body)
            self.assertEqual(method, "GET")
            caller_request.clear()
            caller_request.update(other)
            return observed

        with mock.patch.object(native, "_http", side_effect=mutate_after_real_get):
            recovered = gate.reconcile(caller_request)
        self.assertEqual(caller_request, other)
        self.assertEqual(recovered["state"], "SETTLED")
        self.assertEqual(recovered["request_digest"], original_proof["request_digest"])
        self.assertEqual(recovered["mock_admission"]["request_digest"], original_proof["request_digest"])
        self.assertEqual(recovered["mock_admission"]["proof_digest"], original_proof["record_digest"])
        runtime.verify_receipt(recovered["receipt_bytes"], runtime.request_bytes(original),
                               self.h.key.public_key().public_bytes_raw())

        caller_request.clear()
        caller_request.update(original)
        genuine_read = native.read_status

        def mutate_after_local_read(request):
            result = genuine_read(request)
            caller_request.clear()
            caller_request.update(other)
            return result

        with mock.patch.object(native, "read_status", side_effect=mutate_after_local_read):
            cached = gate.read_status(caller_request)
        self.assertEqual(cached["mock_admission"]["request_digest"], original_proof["request_digest"])
        self.assertEqual(cached["mock_admission"]["proof_digest"], original_proof["record_digest"])
        self.assertEqual(self.h.counts()["post_attempts"], 2)
        self.assertEqual(self.h.counts()["effects"], 2)
        self.assertEqual(self.rows(), {"claims": 2, "proofs": 2})

    def test_historical_recheck_detects_altered_proof_even_with_recomputed_outer_digest(self):
        gate = self.h.gate()
        settled = gate.submit(self.h.request, self.h.evidence)
        original = gate.read_authorization(self.h.request)
        checked = authorization.recheck_record(original["record_bytes"])
        self.assertEqual(checked["verdict"], "SUPPORTED")
        self.assertIs(checked["current_authorization_asserted"], False)
        self.assertIs(checked["independent_trust_established"], False)
        # Trusted fault injection deliberately removes the local SQL guard. This
        # checks internal historical coherence, not malicious-host resistance.
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            db.execute("DROP TRIGGER immutable_authorization_proof_update")
            db.commit()
        for fault in ("original_signature", "decision", "freshness_parameter"):
            with self.subTest(fault=fault):
                packed = authorization.load_json(original["record_bytes"])
                if fault == "original_signature":
                    envelope = authorization.load_json(bytes.fromhex(packed["evidence"]["maker_approval"]))
                    envelope["payload"]["approval_id"] = "altered-after-original-signature"
                    packed["evidence"]["maker_approval"] = authorization.canonical_json(envelope).hex()
                elif fault == "decision":
                    packed["decision"]["reasons"] = ["forged_authorized_label"]
                else:
                    packed["max_status_age_ms"] = 1
                raw = authorization.canonical_json(packed)
                self.assertEqual(authorization.recheck_record(raw)["verdict"], "UNVERIFIABLE")
                with closing(sqlite3.connect(self.h.journal_path)) as db:
                    db.execute("UPDATE authorization_proofs SET record_bytes=?,record_digest=?", (
                        raw, authorization.bytes_digest(raw)))
                    db.commit()
                self.assertEqual(gate.read_authorization(self.h.request)["status"], "UNAVAILABLE")
                cached = gate.read_status(self.h.request)
                self.assertEqual(cached["state"], "SETTLED")
                self.assertEqual(cached["receipt_bytes"], settled["receipt_bytes"])
                self.assertEqual(cached["mock_admission"]["verdict"], "UNKNOWN")
                self.assertEqual(gate.submit(self.h.request, self.h.evidence)["mock_admission"]["verdict"], "UNKNOWN")
                self.assert_one_effect()
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            db.execute("UPDATE authorization_proofs SET record_bytes=?,record_digest=?", (
                original["record_bytes"], original["record_digest"]))
            db.commit()
        self.assertEqual(gate.read_authorization(self.h.request)["status"], "FOUND")


if __name__ == "__main__":
    unittest.main()
